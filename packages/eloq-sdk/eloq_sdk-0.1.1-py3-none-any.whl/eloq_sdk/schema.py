# Generated from Eloq API swagger definitions
# Based on swagger.yaml structure

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Dict, Any

try:
    from pydantic.dataclasses import dataclass
except ImportError:
    from dataclasses import dataclass


@dataclass
class ShelfResponse:
    """Base API response structure."""
    code: int
    data: Any
    message: str


@dataclass
class Pagination:
    """Pagination information."""
    cursor: str


@dataclass
class EmptyResponse:
    """Empty response."""
    pass


# Billing related models
@dataclass
class EloqShelfPricePlan:
    """Price plan information."""
    base_price: float
    billing_period: str  # monthly, annual
    currency: str
    description: str
    included_compute_hours: float
    included_compute_unlimited: bool
    included_cu_capacity: int
    included_network_gb: float
    included_network_unlimited: bool
    included_projects: int
    included_storage_gb: float
    included_storage_unlimited: bool
    is_public: bool
    plan_name: str


@dataclass
class EloqShelfOveragePricing:
    """Overage pricing information."""
    max_usage: float
    min_usage: float
    price_per_unit: float
    resource_type: int
    tier_level: int
    unit_description: str


@dataclass
class DataBaseAndOveragePlan:
    """Combined base plan and overage plan."""
    base_plan: EloqShelfPricePlan
    overage_plan: EloqShelfOveragePricing


@dataclass
class SubscribePlanBody:
    """Subscribe plan request body."""
    plan_id: int


# Cluster related models
@dataclass
class ClusterListItem:
    """Cluster list item information."""
    cloud_provider: str
    cluster_name: str
    create_at: str
    module_type: str
    region: str
    status: str
    version: str
    zone: str


@dataclass
class DescClusterDTO:
    """Detailed cluster information."""
    admin_password: str
    admin_user: str
    cloud_provider: str
    cluster_deploy_mode: str
    create_at: str
    display_cluster_name: str
    elb_addr: str
    elb_port: int
    elb_state: str
    log_cpu_limit: float
    log_memory_mi_limit: float
    log_replica: int
    module_type: str
    org_name: str
    project_name: str
    region: str
    status: str
    tx_cpu_limit: float
    tx_memory_mi_limit: float
    tx_replica: int
    version: str
    zone: str


class ServiceType(Enum):
    """Service type enumeration."""
    LOG = "log"
    TX = "tx"
    ALL = "all"


class ClusterOperation(Enum):
    """Cluster operation types."""
    START = "start"
    SHUTDOWN = "shutdown"
    RESTART = "restart"


# Dashboard related models
@dataclass
class DashboardType:
    """Dashboard type information."""
    interval: bool
    name: str
    percentile: Optional[float] = None


# Organization related models - Updated based on swagger.yaml
@dataclass
class SimpleProjectInfo:
    """Simple project information."""
    create_at: str
    project_id: int
    project_name: str


@dataclass
class OrgInfo:
    """Organization information."""
    org_create_at: str
    org_id: int
    org_name: str
    projects: List[SimpleProjectInfo]
    roles: List[str]


@dataclass
class UserOrgInfoDTO:
    """User organization information - Updated based on swagger.yaml."""
    auth_provider: str
    create_at: str
    email: str
    org_info: OrgInfo
    user_name: str


# Request body models
@dataclass
class CreateClusterBody:
    """Create cluster request body."""
    cluster_name: str
    cloud_provider: str
    region: str
    zone: str
    module_type: str
    version: str
    display_cluster_name: str
    cluster_deploy_mode: str
    log_cpu_limit: float
    log_memory_mi_limit: float
    log_replica: int
    tx_cpu_limit: float
    tx_memory_mi_limit: float
    tx_replica: int


@dataclass
class OpClusterBody:
    """Cluster operation request body."""
    # This can be empty for some operations
    pass


# Node type related models
@dataclass
class NodeTypeInfo:
    """Node type information."""
    cloud_provider: str
    module_type: str
    service_type: str
    node_type: str
    spot: Optional[bool] = None


# Simplified organization model
@dataclass
class SimpleOrgInfo:
    """Simplified organization information."""
    org_name: str
    org_id: int
    org_create_at: str


# Cluster credentials model
@dataclass
class ClusterCredentials:
    """Cluster credentials for database connection."""
    username: str
    password: str
    host: str
    port: int
    status: str
