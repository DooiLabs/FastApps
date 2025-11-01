"""Data models for FastApps Cloud API responses."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserInfo:
    """User information from /api/me."""

    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    github_username: Optional[str] = None


@dataclass
class DeploymentListItem:
    """Deployment list item from /api/deployments."""

    id: str
    projectId: Optional[str]
    status: str
    domain: Optional[str]
    url: Optional[str]
    createdAt: str


@dataclass
class DeploymentResponse:
    """Detailed deployment information from /api/deployments/{id}."""

    id: str
    userId: str
    projectId: Optional[str]
    status: str
    domain: Optional[str]
    url: Optional[str]
    deploymentId: Optional[str]
    blobSize: Optional[int]
    createdAt: str
    updatedAt: str


@dataclass
class ProjectInfo:
    """Project information from /api/projects."""

    projectId: str
    deployment_count: int
    latest_status: Optional[str]
    latest_domain: Optional[str]
    last_deployed: Optional[str]


@dataclass
class ProjectDetail:
    """Detailed project information from /api/projects/{id}."""

    projectId: str
    deployments: list[DeploymentListItem]
