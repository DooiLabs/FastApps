"""HTTP client for FastApps deployment API."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import httpx


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    success: bool
    deployment_url: Optional[str] = None
    deployment_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    status: Optional[str] = None
    domain: Optional[str] = None


class DeployClient:
    """Client for interacting with FastApps deployment server."""

    def __init__(self, base_url: str, access_token: str, project_id: str = "default"):
        """
        Initialize deployment client.

        Args:
            base_url: Base URL of deployment server
            access_token: OAuth access token
            project_id: Project identifier for deployment
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.project_id = project_id
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialized HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
        return self._client

    async def deploy(
        self,
        tarball_path: Path,
        max_poll_attempts: int = 60,
        poll_interval: int = 5,
        status_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> DeploymentResult:
        """
        Deploy artifact to server and poll until completion.

        Args:
            tarball_path: Path to deployment tarball
            max_poll_attempts: Maximum number of status checks (default: 60)
            poll_interval: Seconds between status checks (default: 5)
            status_callback: Optional callback function(status, attempt, max_attempts)

        Returns:
            DeploymentResult with deployment information

        Raises:
            RuntimeError: If deployment fails
        """
        try:
            # Read tarball content to avoid file handle issues
            with open(tarball_path, "rb") as f:
                file_content = f.read()

            files = {"file": ("deployment.tar.gz", file_content, "application/gzip")}
            data = {"project_id": self.project_id}

            # Send deployment request
            response = await self.client.post(
                f"{self.base_url}/api/deployments",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                deployment = response_data.get("deployment", {})
                deployment_id = deployment.get("id")

                if not deployment_id:
                    return DeploymentResult(
                        success=False,
                        error="Invalid response: missing deployment ID",
                    )

                # Poll deployment status
                return await self._poll_deployment_status(
                    deployment_id, max_poll_attempts, poll_interval, status_callback
                )

            elif response.status_code == 401:
                return DeploymentResult(
                    success=False,
                    error="Authentication failed. Please run 'fastapps deploy' again to re-authenticate.",
                )
            elif response.status_code == 400:
                # Fix: Check if content-type contains json (handles charset)
                content_type = response.headers.get("content-type", "")
                data = response.json() if "application/json" in content_type else {}
                error_msg = data.get("error", response.text)
                return DeploymentResult(
                    success=False,
                    error=f"Invalid deployment package: {error_msg}",
                )
            else:
                return DeploymentResult(
                    success=False,
                    error=f"Deployment failed: {response.status_code} - {response.text}",
                )

        except httpx.ConnectError as e:
            return DeploymentResult(
                success=False,
                error=f"Connection error: Cannot reach deployment server",
            )
        except httpx.TimeoutException as e:
            return DeploymentResult(
                success=False,
                error=f"Network timeout: Request took too long",
            )
        except httpx.RequestError as e:
            return DeploymentResult(
                success=False,
                error=f"Network error during deployment: {e}",
            )
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=f"Unexpected error: {e}",
            )

    async def _poll_deployment_status(
        self,
        deployment_id: str,
        max_attempts: int,
        interval: int,
        status_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> DeploymentResult:
        """
        Poll deployment status until completion or failure.

        Args:
            deployment_id: Deployment ID to check
            max_attempts: Maximum polling attempts
            interval: Seconds between attempts
            status_callback: Optional callback function(status, attempt, max_attempts)

        Returns:
            DeploymentResult with final status
        """
        for attempt in range(max_attempts):
            await asyncio.sleep(interval)

            try:
                response = await self.client.get(
                    f"{self.base_url}/api/deployments/{deployment_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )

                if response.status_code != 200:
                    continue

                data = response.json()
                status = data.get("status")
                domain = data.get("domain")

                # Call status callback if provided
                if status_callback:
                    status_callback(status, attempt + 1, max_attempts)

                if status == "deployed":
                    deployment_url = f"https://{domain}" if domain else None
                    return DeploymentResult(
                        success=True,
                        deployment_id=deployment_id,
                        deployment_url=deployment_url,
                        domain=domain,
                        status=status,
                        message="Deployment completed successfully",
                    )
                elif status == "failed":
                    error_msg = data.get("error", "Deployment failed")
                    return DeploymentResult(
                        success=False,
                        deployment_id=deployment_id,
                        status=status,
                        error=error_msg,
                    )

            except Exception as e:
                # Continue polling on transient errors
                continue

        # Timeout
        return DeploymentResult(
            success=False,
            deployment_id=deployment_id,
            error=f"Deployment timeout: still in progress after {max_attempts * interval} seconds",
        )

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
