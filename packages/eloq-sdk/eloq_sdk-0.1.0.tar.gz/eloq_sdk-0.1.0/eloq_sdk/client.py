import json
import os
import typing as t
from datetime import datetime
from functools import wraps

import requests

from . import schema
from .utils import compact_mapping, to_iso8601
from .exceptions import (
    EloqAPIError, 
    EloqAuthenticationError, 
    EloqPermissionError, 
    EloqNotFoundError, 
    EloqRateLimitError, 
    EloqServerError, 
    EloqValidationError
)


__VERSION__ = "0.1.0"

ELOQ_API_KEY_ENVIRON = "ELOQ_API_KEY"
ELOQ_API_BASE_URL = "https://api.eloqdata.com/api/v1/"
ENABLE_PYDANTIC = True


def returns_model(model, is_array=False):
    """Decorator that returns a Pydantic dataclass.

    :param model: The Pydantic dataclass to return.
    :param is_array: Whether the return value is an array (default is False).
    :return: A Pydantic dataclass.

    If Pydantic is not enabled, the original return value is returned.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not ENABLE_PYDANTIC:
                return func(*args, **kwargs)

            result = func(*args, **kwargs)
            
            if is_array:
                return [model(**item) if isinstance(item, dict) else item for item in result]
            else:
                return model(**result) if isinstance(result, dict) else result

        return wrapper

    return decorator


def returns_subkey(key):
    """Decorator that returns a subkey.

    :param key: The key to return.
    :return: The value of the key in the return value.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                try:
                    return getattr(result, key)
                except AttributeError:
                    return result[key]
            except EloqAPIError:
                # Re-raise EloqAPIError without modification to avoid duplicate error messages
                raise

        return wrapper

    return decorator


class EloqAPI:
    def __init__(self, api_key: str, *, base_url: str = None):
        """A Eloq API client.

        :param api_key: The API key to use for authentication.
        :param base_url: The base URL of the Eloq API (default is https://api.eloq.com/api/v1/).
        """

        # Set the base URL.
        if not base_url:
            base_url = ELOQ_API_BASE_URL

        # Private attributes.
        self._api_key = api_key
        self._session = requests.Session()

        # Public attributes.
        self.base_url = base_url
        self.user_agent = f"eloq-client/python version=({__VERSION__})"

    def __repr__(self):
        return f"<EloqAPI base_url={self.base_url!r}>"

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ):
        """Send an HTTP request to the specified API path using the specified method.

        :param method: The HTTP method to use (e.g., "GET", "POST", "PUT", "DELETE").
        :param path: The API path to send the request to.
        :param kwargs: Additional keyword arguments to pass to the requests.Session.request method.
        :return: The JSON response from the server.
        """

        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        # Send the request.
        r = self._session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )

        # Check the response status code.
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Parse the error response
            try:
                error_data = r.json()
            except (ValueError, json.JSONDecodeError):
                error_data = {"message": r.text, "code": r.status_code}
            
            # Create appropriate exception based on status code
            if r.status_code == 401:
                raise EloqAuthenticationError(r.text, r.status_code, error_data)
            elif r.status_code == 403:
                raise EloqPermissionError(r.text, r.status_code, error_data)
            elif r.status_code == 404:
                raise EloqNotFoundError(r.text, r.status_code, error_data)
            elif r.status_code == 429:
                raise EloqRateLimitError(r.text, r.status_code, error_data)
            elif r.status_code >= 500:
                raise EloqServerError(r.text, r.status_code, error_data)
            elif r.status_code == 400:
                raise EloqValidationError(r.text, r.status_code, error_data)
            else:
                raise EloqAPIError(r.text, r.status_code, error_data)

        return r.json()

    def _url_join(self, *args):
        """Join a list of URL components into a single URL."""

        return "/".join(args)

    @classmethod
    def from_environ(cls):
        """Create a new Eloq API client from the `ELOQ_API_KEY` environment variable."""

        return cls(os.environ[ELOQ_API_KEY_ENVIRON])

    @classmethod
    def from_token(cls, token: str):
        """Create a new Eloq API client from a token."""

        return cls(token)

    # Organization and Project Management
    @returns_model(schema.UserOrgInfoDTO)
    @returns_subkey("data")
    def org_info(self) -> t.Dict[str, t.Any]:
        """Get organization and related project info.

        More info: Get current user's organization information
        """

        return self._request("GET", "org-info")

    @returns_model(schema.SimpleProjectInfo, is_array=True)
    def projects(self) -> t.List[t.Dict[str, t.Any]]:
        """Get all projects in the current user's organization.

        This function extracts project information from the user's organization info.
        It's a convenience method that calls org_info() and returns the projects list.

        :return: A list of dataclasses representing the projects in the organization.

        Example usage:

            >>> projects = client.projects()
            >>> for project in projects:
            ...     print(f"Project: {project.project_name} (ID: {project.project_id})")
            ...     print(f"Created: {project.create_at}")

        More info: Get projects from organization info
        """

        org_info = self.org_info()
        return org_info.org_info.projects

    @returns_model(schema.SimpleOrgInfo)
    def org(self) -> schema.SimpleOrgInfo:
        """Get simplified organization information.

        This function calls the org_info() method and extracts only the basic
        organization details for simplified access.

        :return: A SimpleOrgInfo object containing basic organization information.

        Example usage:

            >>> org = client.org()
            >>> print(f"Organization: {org.org_name}")
            >>> print(f"ID: {org.org_id}")
            >>> print(f"Created: {org.org_create_at}")

        More info: Get simplified organization info
        """

        org_info = self.org_info()
        
        # Return SimpleOrgInfo object
        return {
            "org_name": org_info.org_info.org_name,
            "org_id": org_info.org_info.org_id,
            "org_create_at": org_info.org_info.org_create_at
        }

    # Cluster Management
    @returns_model(schema.ClusterListItem, is_array=True)
    @returns_subkey("data")
    def clusters(
        self,
        org_id: int,
        project_id: int,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of clusters in a project.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param page: The page number for pagination (default is 1).
        :param per_page: The number of items per page (default is 20).
        :return: A list of dataclasses representing the clusters.

        More info: List clusters in a project
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters"
        r_params = compact_mapping({"page": page, "perPage": per_page})

        return self._request("GET", r_path, params=r_params)

    @returns_model(schema.DescClusterDTO)
    @returns_subkey("data")
    def cluster(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> t.Dict[str, t.Any]:
        """Get detailed information about a cluster.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the cluster details.

        More info: Describe cluster
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}"

        return self._request("GET", r_path)

    @returns_model(schema.ShelfResponse)
    def cluster_create(
        self,
        org_id: int,
        project_id: int,
        **json: dict,
    ) -> t.Dict[str, t.Any]:
        """Create a new cluster in a project.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param json: The JSON payload to send to the server.
        :return: A dataclass representing the response.

        Example usage:

            >>> eloq.cluster_create(
            ...     org_id=123,
            ...     project_id=456,
            ...     cluster_name="my-cluster",
            ...     cloud_provider="aws",
            ...     region="us-west-2",
            ...     zone="us-west-2a",
            ...     module_type="eloqkv",
            ...     version="1.0.0",
            ...     display_cluster_name="My Cluster",
            ...     cluster_deploy_mode="standard",
            ...     log_cpu_limit=1.0,
            ...     log_memory_mi_limit=1024,
            ...     log_replica=3,
            ...     tx_cpu_limit=2.0,
            ...     tx_memory_mi_limit=2048,
            ...     tx_replica=3
            ... )

        More info: Create cluster in a project
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters"

        return self._request("POST", r_path, json=json)

    @returns_model(schema.ShelfResponse)
    def cluster_operation(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
        operation: str,
        **json: dict,
    ) -> t.Dict[str, t.Any]:
        """Perform an operation on a cluster (start, stop, restart).

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :param operation: The operation to perform (start, shutdown, restart).
        :param json: The JSON payload to send to the server.
        :return: A dataclass representing the response.

        Example usage:

            >>> eloq.cluster_operation(123, 456, "my-cluster", "start")
            >>> eloq.cluster_operation(123, 456, "my-cluster", "shutdown")
            >>> eloq.cluster_operation(123, 456, "my-cluster", "restart")

        More info: Start, stop or restart cluster
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}/{operation}"

        return self._request("POST", r_path, json=json)

    @returns_model(schema.ShelfResponse)
    def cluster_config_history(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> t.Dict[str, t.Any]:
        """Get configuration history for a cluster.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the response.

        More info: List config history
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}/config-history"

        return self._request("GET", r_path)

    @returns_model(schema.ShelfResponse)
    def cluster_apply_config(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
        config_id: int,
    ) -> t.Dict[str, t.Any]:
        """Apply a configuration to a cluster and restart it.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :param config_id: The configuration ID to apply.
        :return: A dataclass representing the response.

        More info: Apply actual CR resource config and restart cluster
        """

        r_path = f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}/configs/{config_id}/apply"

        return self._request("POST", r_path)

    # Billing Management
    @returns_model(schema.DataBaseAndOveragePlan)
    def user_subscription(self) -> t.Dict[str, t.Any]:
        """Get user plan subscription.

        :return: A dataclass representing the user's subscription.

        More info: Get user plan subscription
        """

        return self._request("GET", "billing/user-subscription")

    @returns_model(schema.DataBaseAndOveragePlan, is_array=True)
    def list_pricing_plans(self) -> t.List[t.Dict[str, t.Any]]:
        """List all available pricing plans.

        :return: A list of dataclasses representing the pricing plans.

        More info: List pricing plans
        """

        return self._request("GET", "billing/list-pricing-plans")

    @returns_model(schema.ShelfResponse)
    def subscribe_plan(self, plan_id: int) -> t.Dict[str, t.Any]:
        """Subscribe to a plan.

        :param plan_id: The ID of the plan to subscribe to.
        :return: A dataclass representing the response.

        More info: Subscribe plan
        """

        json_data = {"planId": plan_id}

        return self._request("POST", "billing/subscribe-plan", json=json_data)

    # Dashboard
    @returns_model(schema.DashboardType, is_array=True)
    @returns_subkey("data")
    def dashboard_info(
        self,
        *,
        product_type: str = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get dashboard information.

        :param product_type: EloqCluster Product Type Enum (EloqKV, EloqSQL).
        :return: A list of dataclasses representing dashboard types.

        More info: Get dashboard info
        """

        r_params = compact_mapping({"productType": product_type})

        return self._request("GET", "dashboard/info", params=r_params)

    # Convenience methods for cluster operations
    def start_cluster(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> t.Dict[str, t.Any]:
        """Start a cluster.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the response.
        """

        return self.cluster_operation(org_id, project_id, cluster_name, "start")

    def stop_cluster(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> t.Dict[str, t.Any]:
        """Stop a cluster.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the response.
        """

        return self.cluster_operation(org_id, project_id, cluster_name, "shutdown")

    def restart_cluster(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> t.Dict[str, t.Any]:
        """Restart a cluster.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the response.
        """

        return self.cluster_operation(org_id, project_id, cluster_name, "restart")

    @returns_model(schema.ClusterCredentials)
    def cluster_credentials(
        self,
        org_id: int,
        project_id: int,
        cluster_name: str,
    ) -> schema.ClusterCredentials:
        """Get cluster credentials (username and password) for database connection.

        This function calls the cluster() method and extracts the admin credentials
        for easy access to database connection information.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param cluster_name: The name of the cluster.
        :return: A ClusterCredentials object containing cluster credentials and connection info.

        Example usage:

            >>> credentials = client.cluster_credentials(1, 147, "my-cluster")
            >>> print(f"Username: {credentials.username}")
            >>> print(f"Password: {credentials.password}")
            >>> print(f"Host: {credentials.host}")
            >>> print(f"Port: {credentials.port}")

        More info: Get cluster credentials for database connection
        """

        cluster_info = self.cluster(org_id, project_id, cluster_name)
        
        # Return ClusterCredentials object
        return {
            "username": cluster_info.admin_user,
            "password": cluster_info.admin_password,
            "host": cluster_info.elb_addr,
            "port": cluster_info.elb_port,
            "status": cluster_info.status,
        }
