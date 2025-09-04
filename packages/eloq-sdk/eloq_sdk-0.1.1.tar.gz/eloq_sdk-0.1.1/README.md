# SDK Package

```
eloq_api/
├── __init__.py          # Package initialization and factory functions
├── __version__.py       # Version information
├── client.py            # Core API client
├── schema.py            # Data model definitions
├── exceptions.py        # Custom exception classes
└── utils.py             # Utility functions
```

# **Feature Coverage Comparison**
| Feature Category | Nxxx API | Eloq API | Coverage |
| --- | --- | --- | --- |
| Basic Authentication | ✅ | ✅ | 100% |
| Organization Management | ✅ | ✅ | 100% |
| Cluster Management | ✅ | ✅ | 50% |
| Database Management| ✅ | ❌ | 0%  (base on Branch)|
| Branch Management | ✅ | ❌ | 0% |
| Monitoring Queries | ✅ | ✅ | 100% |
| Billing Management | ✅ | ✅ | 100% |
| Integration Extensions | ✅ | ❌ | 0% |


# SDK API Reference

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Client Initialization](#client-initialization)
- [Core API Methods](#core-api-methods)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Installation

### Local

```bash
pip install -e .
```

### pip

```bash
pip install eloq-sdk
```

## Quick Start

```python
from eloq_sdk import EloqAPI

# Create client with token
client = EloqAPI.from_token("your_api_token")

# Or create from environment variable
client = EloqAPI.from_environ()
```

## Client Initialization

### `EloqAPI.from_environ()`
Create client from `ELOQ_API_KEY` environment variable.

**Example:**
```bash
export ELOQ_API_KEY="your_api_key"
```
```python
client = EloqAPI.from_environ()
```

### `EloqAPI.from_token(token: str)`
Create client from token string.

**Parameters:**
- `token` (str): Your Eloq API token

**Example:**
```python
client = EloqAPI.from_token("your_token_here")
```

## Core API Methods

**📚 Quick Navigation - Click to jump to function details:**

**Organization Management**
- [`org()`](#org---simpleorginfo)
- [`org_info()`](#org_info---userorginfodto)

**Project Management:**
- [`projects()`](#projects---listsimpleprojectinfo)

**Cluster Management:**
- [`cluster_credentials()`](#cluster_credentialsorg_id-int-project_id-int-cluster_name-str---clustercredentials)
- [`cluster()`](#clusterorg_id-int-project_id-int-cluster_name-str---descclusterdto)
- [`clusters()`](#clustersorg_id-int-project_id-int--page-int--1-per_page-int--20---listclusterlistitem)
- [`cluster_create()`](#cluster_createorg_id-int-project_id-int-json-dict---shelfresponse)
- [`cluster_operation()`](#cluster_operationorg_id-int-project_id-int-cluster_name-str-operation-str-json-dict---shelfresponse)
- [`cluster_config_history()`](#cluster_config_historyorg_id-int-project_id-int-cluster_name-str---shelfresponse)

**Convenience Methods for Cluster Operations:**
- [`start_cluster()`](#start_clusterorg_id-int-project_id-int-cluster_name-str---shelfresponse)
- [`stop_cluster()`](#stop_clusterorg_id-int-project_id-int-cluster_name-str---shelfresponse)
- [`restart_cluster()`](#restart_clusterorg_id-int-project_id-int-cluster_name-str---shelfresponse)


**Billing Management:**
- [`user_subscription()`](#user_subscription---databaseandoverageplan)
- [`list_pricing_plans()`](#list_pricing_plans---listdatabaseandoverageplan)
- [`subscribe_plan()`](#subscribe_planplan_id-int---shelfresponse)

**Dashboard Information:**
- [`dashboard_info()`](#dashboard_infoproduct_type-str--none---listdashboardtype)

---

### Organization & Project Management

#### `org_info() -> UserOrgInfoDTO`
Get current user's organization information.

**Returns:** `UserOrgInfoDTO` object with the following structure:
- `auth_provider` (str): Authentication provider (e.g., "github")
- `create_at` (str): User account creation timestamp (e.g., "2025-08-20 08:20:21")
- `email` (str): User email address (e.g., "1111111@mail.com")
- `org_info` (OrgInfo): Organization information object
- `user_name` (str): Username (e.g., "1976263299")

**OrgInfo Object Fields:**
- `org_create_at` (str): Organization creation timestamp (e.g., "2025-05-14 13:51:02")
- `org_id` (int): Organization ID (e.g., 1)
- `org_name` (str): Organization name (e.g., "default-free-org")
- `projects` (List[SimpleProjectInfo]): List of projects in the organization
- `roles` (List[str]): User roles in the organization (e.g., ["project-owner", "cluster-owner"])

**SimpleProjectInfo Object Fields:**
- `create_at` (str): Project creation timestamp (e.g., "2025-08-20 08:20:21")
- `project_id` (int): Project ID (e.g., 147)
- `project_name` (str): Project name (e.g., "project1")

**Example:**
```python
org_info = client.org_info()
print(f"Organization: {org_info.org_info.org_name}")
print(f"User: {org_info.user_name}")
```

#### `org() -> SimpleOrgInfo`
Get simplified organization information.

This function calls the `org_info()` method and extracts only the basic
organization details for simplified access.

**Returns:** `SimpleOrgInfo` object containing basic organization information:
- `org_name` (str): Organization name (e.g., "default-free-org")
- `org_id` (int): Organization ID (e.g., 1)
- `org_create_at` (str): Organization creation timestamp (e.g., "2025-05-14 13:51:02")

**Example:**
```python
org = client.org()
print(f"Organization: {org.org_name}")
print(f"ID: {org.org_id}")
print(f"Created: {org.org_create_at}")
```

#### `projects() -> List[SimpleProjectInfo]`
Get all projects in the current user's organization.

This function extracts project information from the user's organization info.
It's a convenience method that calls `org_info()` and returns the projects list.

**Returns:** `List[SimpleProjectInfo]` - List of project information objects, each containing:
- `create_at` (str): Project creation timestamp (e.g., "2025-08-20 08:20:21")
- `project_id` (int): Project ID (e.g., 147)
- `project_name` (str): Project name (e.g., "1976263299-qq.com-pro")

**Example:**
```python
projects = client.projects()
for project in projects:
    print(f"Project: {project.project_name} (ID: {project.project_id})")
    print(f"Created: {project.create_at}")
```



### Cluster Management


#### `cluster_credentials(org_id: int, project_id: int, cluster_name: str) -> ClusterCredentials`
Get cluster credentials (username and password) for database connection.

This function calls the `cluster()` method and extracts the admin credentials
for easy access to database connection information.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `ClusterCredentials` object containing cluster credentials and connection info:
- `username` (str): Base64 encoded admin username for the cluster
- `password` (str): Base64 encoded admin password for the cluster
- `host` (str): Elastic Load Balancer address for connection
- `port` (int): Elastic Load Balancer port for connection
- `status` (str): Cluster status (e.g., "idle")

**Example:**
```python
credentials = client.cluster_credentials(1, 147, "my-cluster")
print(f"Username: {credentials.username}")
print(f"Password: {credentials.password}")
print(f"Host: {credentials.host}")
print(f"Port: {credentials.port}")
```



#### `clusters(org_id: int, project_id: int, *, page: int = 1, per_page: int = 20) -> List[ClusterListItem]`
Get a list of clusters in a project.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `page` (int, optional): Page number for pagination (default: 1)
- `per_page` (int, optional): Items per page (default: 20)

**Returns:** `List[ClusterListItem]` - List of cluster information objects, each containing:
- `cloud_provider` (str): Cloud provider name (e.g., "AWS")
- `cluster_name` (str): Name of the cluster (e.g., "test-cluster-123", "nihhhh", "nihhhhop")
- `create_at` (str): Cluster creation timestamp in ISO format (e.g., "2025-08-26T08:06:41Z")
- `module_type` (str): Module type (e.g., "EloqKV")
- `region` (str): Cloud region (e.g., "us-west-1")
- `status` (str): Cluster status (e.g., "idle")
- `version` (str): Cluster version (e.g., "nightly-2025-05-16")
- `zone` (str): Cloud zone (e.g., "us-west-1a")

**Example:**
```python
clusters = client.clusters(org_id=123, project_id=456)
for cluster in clusters:
    print(f"Cluster: {cluster.cluster_name}, Status: {cluster.status}")
```



#### `cluster(org_id: int, project_id: int, cluster_name: str) -> DescClusterDTO`
Get detailed information about a specific cluster.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `DescClusterDTO` object with detailed cluster information including:
- `admin_password` (str): Base64 encoded admin password for the cluster (e.g., "cHFzRTZoT3JyMjlqL2ZqM29nczVyc0hESTdbMW1kNkhjTmRrV0w5SW52cz0=")
- `admin_user` (str): Base64 encoded admin username for the cluster (e.g., "MTQ1LW5paGhOaA==")
- `cloud_provider` (str): Cloud provider name (e.g., "aws")
- `cluster_deploy_mode` (str): Cluster deployment mode (e.g., "txWithInternalLog")
- `create_at` (str): Cluster creation timestamp in ISO format (e.g., "2025-08-25T10:09:15Z")
- `display_cluster_name` (str): Display name of the cluster (e.g., "eloqdb")
- `elb_addr` (str): Elastic Load Balancer address (e.g., "k8s-eloqkvpr-uswest1a-59c3f9a165-fdf95696be734561.elb.us-west-1.amazonaws.com")
- `elb_port` (int): Elastic Load Balancer port (e.g., 6378)
- `elb_state` (str): Elastic Load Balancer state (e.g., "active")
- `log_cpu_limit` (float): Log service CPU limit (e.g., 0.0)
- `log_memory_mi_limit` (float): Log service memory limit in Mi (e.g., 0.0)
- `log_replica` (int): Log service replica count (e.g., 0)
- `module_type` (str): Module type (e.g., "EloqKV")
- `org_name` (str): Organization name (e.g., "default-free-org")
- `project_name` (str): Project name (e.g., "1976263299-qq.com-pro")
- `region` (str): Cloud region (e.g., "us-west-1")
- `status` (str): Cluster status (e.g., "idle")
- `tx_cpu_limit` (float): Transaction service CPU limit (e.g., 0.0)
- `tx_memory_mi_limit` (float): Transaction service memory limit in Mi (e.g., 0.0)
- `tx_replica` (int): Transaction service replica count (e.g., 1)
- `version` (str): Cluster version (e.g., "nightly-2025-05-16")
- `zone` (str): Cloud zone (e.g., "us-west-1a")


**Example:**
```python
cluster_details = client.cluster(org_id=123, project_id=456, cluster_name="my-cluster")
print(f"Cloud Provider: {cluster_details.cloud_provider}")
print(f"Region: {cluster_details.region}")
```



#### `cluster_create(org_id: int, project_id: int, **json: dict) -> ShelfResponse`
Create a new cluster in a project.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name`(string): Name of the cluster
- `region`(string): Cloud region
- `requiredZone`(string): Cloud zone
- `skuId`(int): sku type id

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (usually cluster creation result)
- `message` (str): Response message

**Response Data Fields:**
- `cluster_id` (str): ID of the created cluster
- `cluster_name` (str): Name of the created cluster
- `status` (str): Creation status
- `message` (str): Additional information about the creation

**Example:**
```python
response = client.cluster_create(
        org_id=1,
        project_id=147,
  
        clusterName="test-cluster-123",
        region="us-west-1",
        requiredZone="us-west-1a",
        skuId=1  
)
```



#### `cluster_operation(org_id: int, project_id: int, cluster_name: str, operation: str, **json: dict) -> ShelfResponse`
Perform operations on a cluster (start, stop, restart).

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster
- `operation` (str): Operation to perform ("start", "shutdown", "restart")
- `**json`: Additional operation parameters

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (operation result)
- `message` (str): Response message

**Response Data Fields:**
- `operation` (str): The operation performed
- `cluster_name` (str): Name of the cluster
- `status` (str): Operation status
- `message` (str): Additional information about the operation

**Example:**
```python
# Start cluster
client.cluster_operation(123, 456, "my-cluster", "start")

# Stop cluster
client.cluster_operation(123, 456, "my-cluster", "shutdown")

# Restart cluster
client.cluster_operation(123, 456, "my-cluster", "restart")
```



#### `cluster_config_history(org_id: int, project_id: int, cluster_name: str) -> ShelfResponse`
Get configuration history for a cluster.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (List[Dict]): List of configuration history entries
- `message` (str): Response message

**Response Data Fields (each history entry):**
- `config_id` (int): Configuration ID
- `cluster_name` (str): Name of the cluster
- `config_type` (str): Type of configuration
- `create_at` (str): Configuration creation timestamp
- `status` (str): Configuration status
- `description` (str): Configuration description

**Example:**
```python
config_history = client.cluster_config_history(123, 456, "my-cluster")
```



#### `cluster_apply_config(org_id: int, project_id: int, cluster_name: str, config_id: int) -> ShelfResponse`
Apply a configuration to a cluster and restart it.

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster
- `config_id` (int): Configuration ID to apply

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (configuration application result)
- `message` (str): Response message

**Response Data Fields:**
- `config_id` (int): ID of the applied configuration
- `cluster_name` (str): Name of the cluster
- `status` (str): Application status
- `restart_status` (str): Cluster restart status
- `message` (str): Additional information about the application

**Example:**
```python
response = client.cluster_apply_config(123, 456, "my-cluster", 789)
```

### Convenience Methods for Cluster Operations

#### `start_cluster(org_id: int, project_id: int, cluster_name: str) -> ShelfResponse`
Start a cluster (convenience method).

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (start operation result)
- `message` (str): Response message

**Response Data Fields:**
- `operation` (str): "start"
- `cluster_name` (str): Name of the cluster
- `status` (str): Start operation status
- `message` (str): Additional information about the start operation

**Example:**
```python
client.start_cluster(123, 456, "my-cluster")
```

#### `stop_cluster(org_id: int, project_id: int, cluster_name: str) -> ShelfResponse`
Stop a cluster (convenience method).

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (stop operation result)
- `message` (str): Response message

**Response Data Fields:**
- `operation` (str): "shutdown"
- `cluster_name` (str): Name of the cluster
- `status` (str): Stop operation status
- `message` (str): Additional information about the stop operation

**Example:**
```python
client.stop_cluster(123, 456, "my-cluster")
```

#### `restart_cluster(org_id: int, project_id: int, cluster_name: str) -> ShelfResponse`
Restart a cluster (convenience method).

**Parameters:**
- `org_id` (int): Organization ID
- `project_id` (int): Project ID
- `cluster_name` (str): Name of the cluster

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (restart operation result)
- `message` (str): Response message

**Response Data Fields:**
- `operation` (str): "restart"
- `cluster_name` (str): Name of the cluster
- `status` (str): Restart operation status
- `message` (str): Additional information about the restart operation

**Example:**
```python
client.restart_cluster(123, 456, "my-cluster")
```


### Billing Management

#### `user_subscription() -> DataBaseAndOveragePlan`
Get user plan subscription information.

**Returns:** `DataBaseAndOveragePlan` object with the following structure:
- `base_plan` (EloqShelfPricePlan): Base subscription plan information
- `overage_plan` (EloqShelfOveragePricing): Overage pricing information

**Base Plan Fields (EloqShelfPricePlan):**
- `base_price` (float): Base plan price
- `billing_period` (str): Billing period ("monthly" or "annual")
- `currency` (str): Currency code
- `description` (str): Plan description
- `included_compute_hours` (float): Included compute hours
- `included_compute_unlimited` (bool): Whether compute is unlimited
- `included_cu_capacity` (int): Included CU capacity
- `included_network_gb` (float): Included network GB
- `included_network_unlimited` (bool): Whether network is unlimited
- `included_projects` (int): Number of included projects
- `included_storage_gb` (float): Included storage GB
- `included_storage_unlimited` (bool): Whether storage is unlimited
- `is_public` (bool): Whether plan is public
- `plan_name` (str): Plan name

**Overage Plan Fields (EloqShelfOveragePricing):**
- `max_usage` (float): Maximum usage limit
- `min_usage` (float): Minimum usage threshold
- `price_per_unit` (float): Price per unit for overage
- `resource_type` (int): Resource type identifier
- `tier_level` (int): Pricing tier level
- `unit_description` (str): Description of the unit

**Example:**
```python
subscription = client.user_subscription()
print(f"Plan: {subscription.base_plan.plan_name}")
print(f"Base Price: {subscription.base_plan.base_price}")
```

#### `list_pricing_plans() -> List[DataBaseAndOveragePlan]`
List all available pricing plans.

**Returns:** `List[DataBaseAndOveragePlan]` - List of available pricing plans, each containing:
- `base_plan` (EloqShelfPricePlan): Base subscription plan information
- `overage_plan` (EloqShelfOveragePricing): Overage pricing information

**Base Plan Fields (EloqShelfPricePlan):**
- `base_price` (float): Base plan price
- `billing_period` (str): Billing period ("monthly" or "annual")
- `currency` (str): Currency code
- `description` (str): Plan description
- `included_compute_hours` (float): Included compute hours
- `included_compute_unlimited` (bool): Whether compute is unlimited
- `included_cu_capacity` (int): Included CU capacity
- `included_network_gb` (float): Included network GB
- `included_network_unlimited` (bool): Whether network is unlimited
- `included_projects` (int): Number of included projects
- `included_storage_gb` (float): Included storage GB
- `included_storage_unlimited` (bool): Whether storage is unlimited
- `is_public` (bool): Whether plan is public
- `plan_name` (str): Plan name

**Overage Plan Fields (EloqShelfOveragePricing):**
- `max_usage` (float): Maximum usage limit
- `min_usage` (float): Minimum usage threshold
- `price_per_unit` (float): Price per unit for overage
- `resource_type` (int): Resource type identifier
- `tier_level` (int): Pricing tier level
- `unit_description` (str): Description of the unit

**Example:**
```python
plans = client.list_pricing_plans()
for plan in plans:
    print(f"Plan: {plan.base_plan.plan_name}")
    print(f"Price: {plan.base_plan.base_price} {plan.base_plan.currency}")
```

#### `subscribe_plan(plan_id: int) -> ShelfResponse`
Subscribe to a pricing plan.

**Parameters:**
- `plan_id` (int): ID of the plan to subscribe to

**Returns:** `ShelfResponse` object with the following structure:
- `code` (int): Response status code
- `data` (Any): Response data (subscription result)
- `message` (str): Response message

**Response Data Fields:**
- `subscription_id` (str): ID of the created subscription
- `plan_id` (int): ID of the subscribed plan
- `status` (str): Subscription status
- `message` (str): Additional information about the subscription

**Example:**
```python
response = client.subscribe_plan(plan_id=123)
```

### Dashboard Information

#### `dashboard_info(*, product_type: str = None) -> List[DashboardType]`
Get dashboard information.

**Parameters:**
- `product_type` (str, optional): Filter by product type ("EloqKV", "EloqSQL")

**Returns:** `List[DashboardType]` - List of dashboard type information objects, each containing:
- `interval` (bool): Whether the dashboard has interval data
- `name` (str): Dashboard name
- `percentile` (Optional[float]): Percentile value for the dashboard (if applicable)

**Example:**
```python
# Get all dashboard info
dashboard_info = client.dashboard_info()

# Get specific product type dashboard info
kv_dashboard = client.dashboard_info(product_type="EloqKV")
```

## Data Models

The SDK uses Pydantic dataclasses for data validation and serialization. Key models include:

- **`UserOrgInfoDTO`**: User and organization information
- **`ClusterListItem`**: Basic cluster information
- **`DescClusterDTO`**: Detailed cluster information
- **`ShelfResponse`**: Standard API response structure
- **`DataBaseAndOveragePlan`**: Billing plan information
- **`DashboardType`**: Dashboard configuration

## Error Handling

The SDK raises `EloqAPIError` for API-related errors:

```python
from eloq_sdk_python.exceptions import EloqAPIError

try:
    clusters = client.clusters(org_id=123, project_id=456)
except EloqAPIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

### Complete Cluster Management Workflow

```python
from eloq_sdk_python import EloqAPI

# Initialize client
client = EloqAPI.from_token("your_token")

# Get organization info
org_info = client.org_info()
org_id = org_info.org_info.org_id
project_id = org_info.org_info.projects[0].project_id

# List clusters
clusters = client.clusters(org_id=org_id, project_id=project_id)
print(f"Found {len(clusters)} clusters")

# Create new cluster
response = client.cluster_create(
    org_id=org_id,
    project_id=project_id,
    cluster_name="new-cluster",
    cloud_provider="aws",
    region="us-west-2",
    zone="us-west-2a",
    module_type="eloqkv",
    version="1.0.0"
)

# Start the cluster
client.start_cluster(org_id, project_id, "new-cluster")

# Get cluster details
cluster_details = client.cluster(org_id, project_id, "new-cluster")
print(f"Cluster status: {cluster_details.status}")
```

### Billing Management

```python
# Get current subscription
subscription = client.user_subscription()
print(f"Current plan: {subscription.base_plan.plan_name}")

# List available plans
plans = client.list_pricing_plans()
for plan in plans:
    print(f"Plan: {plan.base_plan.plan_name}")
    print(f"Price: {plan.base_plan.base_price} {plan.base_plan.currency}")
    print(f"Projects: {plan.base_plan.included_projects}")
    print("---")
```

For more examples, see the `examples/` directory in the project.
