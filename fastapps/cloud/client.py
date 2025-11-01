"""HTTP client for FastApps Cloud API."""

import asyncio
from pathlib import Path
from typing import Callable, Optional

import httpx

from .config import CloudConfig
from .models import DeploymentListItem, DeploymentResponse, UserInfo


class CloudClient:
    """Client for interacting with FastApps Cloud API."""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Cloud client.

        Args:
            base_url: Base URL of cloud server (default: from config)
            token: Authentication token (default: from config)
        """
        self.base_url = (base_url or CloudConfig.get_cloud_url()).rstrip("/")
        self.token = token or CloudConfig.get_token()
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialized HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=300.0)
        return self._client

    def _get_headers(self) -> dict:
        """Get authorization headers."""
        if not self.token:
            raise RuntimeError("Not authenticated. Please run 'fastapps cloud login' first.")
        return {"Authorization": f"Bearer {self.token}"}

    # ==================== User API ====================

    async def get_current_user(self) -> UserInfo:
        """
        Get current authenticated user information.

        Returns:
            UserInfo object

        Raises:
            RuntimeError: If not authenticated or request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/me",
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")

            response.raise_for_status()
            data = response.json()

            return UserInfo(
                id=data["id"],
                email=data.get("email"),
                username=data.get("username"),
                github_username=data.get("github_username"),
            )

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    # ==================== Deployment API ====================

    async def create_deployment(
        self,
        tarball_path: Path,
        project_slug: str,
        status_callback: Optional[Callable[[str, int, int], None]] = None,
        max_poll_attempts: int = 60,
        poll_interval: int = 5,
    ) -> DeploymentResponse:
        """
        Create a new deployment and poll until completion.

        Args:
            tarball_path: Path to deployment tarball
            project_slug: Project slug identifier
            status_callback: Optional callback(status, attempt, max_attempts)
            max_poll_attempts: Maximum status checks
            poll_interval: Seconds between checks

        Returns:
            DeploymentResponse object

        Raises:
            RuntimeError: If deployment fails
        """
        try:
            # Upload deployment
            with open(tarball_path, "rb") as f:
                file_content = f.read()

            files = {"file": ("deployment.tar.gz", file_content, "application/gzip")}
            data = {"project_slug": project_slug}

            response = await self.client.post(
                f"{self.base_url}/api/deployments",
                files=files,
                data=data,
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")

            response.raise_for_status()
            response_data = response.json()
            deployment = response_data.get("deployment", {})
            deployment_id = deployment.get("id")

            if not deployment_id:
                raise RuntimeError("Invalid response: missing deployment ID")

            # Poll deployment status
            return await self._poll_deployment_status(
                deployment_id, max_poll_attempts, poll_interval, status_callback
            )

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Deployment error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    async def _poll_deployment_status(
        self,
        deployment_id: str,
        max_attempts: int,
        interval: int,
        status_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> DeploymentResponse:
        """Poll deployment status until completion."""
        for attempt in range(max_attempts):
            await asyncio.sleep(interval)

            try:
                response = await self.client.get(
                    f"{self.base_url}/api/deployments/{deployment_id}",
                    headers=self._get_headers(),
                )

                if response.status_code != 200:
                    continue

                data = response.json()
                status = data.get("status")

                if status_callback:
                    status_callback(status, attempt + 1, max_attempts)

                if status == "deployed":
                    return DeploymentResponse(
                        id=data["id"],
                        userId=data["userId"],
                        projectId=data.get("projectId"),
                        status=status,
                        domain=data.get("domain"),
                        url=data.get("url"),
                        deploymentId=data.get("deploymentId"),
                        blobSize=data.get("blobSize"),
                        createdAt=data["createdAt"],
                        updatedAt=data["updatedAt"],
                    )
                elif status == "failed":
                    error_msg = data.get("error", "Deployment failed")
                    raise RuntimeError(f"Deployment failed: {error_msg}")

            except Exception as e:
                continue

        raise RuntimeError(f"Deployment timeout after {max_attempts * interval} seconds")

    async def list_deployments(self, limit: int = 20) -> list[DeploymentListItem]:
        """
        List deployments for authenticated user.

        Args:
            limit: Maximum number of deployments to return

        Returns:
            List of DeploymentListItem objects

        Raises:
            RuntimeError: If request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/deployments",
                params={"limit": limit},
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")

            response.raise_for_status()
            data = response.json()

            return [
                DeploymentListItem(
                    id=item["id"],
                    projectId=item.get("projectId"),
                    status=item["status"],
                    domain=item.get("domain"),
                    url=item.get("url"),
                    createdAt=item["createdAt"],
                )
                for item in data
            ]

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    async def get_deployment(self, deployment_id: str) -> DeploymentResponse:
        """
        Get detailed deployment information.

        Args:
            deployment_id: Deployment ID

        Returns:
            DeploymentResponse object

        Raises:
            RuntimeError: If deployment not found or request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/deployments/{deployment_id}",
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")
            elif response.status_code == 404:
                raise RuntimeError(f"Deployment {deployment_id} not found")

            response.raise_for_status()
            data = response.json()

            return DeploymentResponse(
                id=data["id"],
                userId=data["userId"],
                projectId=data.get("projectId"),
                status=data["status"],
                domain=data.get("domain"),
                url=data.get("url"),
                deploymentId=data.get("deploymentId"),
                blobSize=data.get("blobSize"),
                createdAt=data["createdAt"],
                updatedAt=data["updatedAt"],
            )

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    async def delete_deployment(self, deployment_id: str) -> bool:
        """
        Delete a deployment.

        Args:
            deployment_id: Deployment ID

        Returns:
            True if deleted successfully

        Raises:
            RuntimeError: If deletion fails
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/deployments/{deployment_id}",
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")
            elif response.status_code == 404:
                raise RuntimeError(f"Deployment {deployment_id} not found")

            response.raise_for_status()
            return True

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    # ==================== Project API ====================

    async def create_project(self, name: str) -> dict:
        """
        Create a new project.

        Args:
            name: Project name

        Returns:
            Project dictionary with id, name, userId

        Raises:
            RuntimeError: If request fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/projects",
                json={"name": name},
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")

            response.raise_for_status()
            data = response.json()
            return data

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    async def list_projects(self) -> list[dict]:
        """
        List all projects for authenticated user.

        Returns:
            List of project dictionaries

        Raises:
            RuntimeError: If request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/projects",
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    async def get_project(self, project_id: str) -> dict:
        """
        Get detailed project information.

        Args:
            project_id: Project ID

        Returns:
            Project dictionary

        Raises:
            RuntimeError: If project not found or request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/projects/{project_id}",
                headers=self._get_headers(),
            )

            if response.status_code == 401:
                raise RuntimeError("Authentication expired. Please run 'fastapps cloud login' again.")
            elif response.status_code == 404:
                raise RuntimeError(f"Project {project_id} not found")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error: {e}")

    # ==================== Cleanup ====================

    async def close(self):
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
