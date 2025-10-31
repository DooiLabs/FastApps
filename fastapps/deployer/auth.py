"""OAuth 2.1 PKCE authentication for FastApps deployment."""

import asyncio
import hashlib
import secrets
import webbrowser
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
import html
import httpx
from aiohttp import web


class Authenticator:
    """Handles OAuth 2.1 PKCE flow for FastApps Cloud authentication."""

    def __init__(self, deploy_url: str):
        """
        Initialize OAuth authenticator.

        Args:
            deploy_url: Base URL of deployment server (e.g., https://deploy.fastapps.org)
        """
        self.deploy_url = deploy_url.rstrip("/")
        self.auth_url = f"{self.deploy_url}/oauth/authorize"
        self.token_url = f"{self.deploy_url}/oauth/token"
        self.redirect_uri = "http://localhost:8765/callback"
        self.client_id = "fastapps-cli"

    def _generate_pkce_pair(self) -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        import base64

        # Generate random code verifier (43-128 characters)
        code_verifier = secrets.token_urlsafe(64)

        # Generate SHA256 code challenge (base64url-encoded per RFC 7636)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            )
            .decode()
            .rstrip("=")
        )

        return code_verifier, code_challenge

    async def authenticate(self, url_callback=None) -> str:
        """
        Perform OAuth PKCE flow to get access token.

        Args:
            url_callback: Optional callback function(url) to receive auth URL

        Returns:
            Access token string

        Raises:
            RuntimeError: If authentication fails
        """
        # Generate PKCE pair
        code_verifier, code_challenge = self._generate_pkce_pair()

        # Start local callback server
        auth_code_future = asyncio.Future()
        app = self._create_callback_app(auth_code_future)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8765)
        await site.start()

        try:
            # Build authorization URL
            auth_params = {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "scope": "deploy",
            }
            auth_full_url = f"{self.auth_url}?{urlencode(auth_params)}"

            # Open browser for user authorization
            webbrowser.open(auth_full_url)

            # Notify callback with auth URL
            if url_callback:
                url_callback(auth_full_url)

            # Wait for callback with timeout
            try:
                auth_code = await asyncio.wait_for(auth_code_future, timeout=300)
            except asyncio.TimeoutError:
                raise RuntimeError("Authentication timed out (5 minutes)")

            # Exchange authorization code for access token
            access_token = await self._exchange_code_for_token(
                auth_code, code_verifier
            )

            return access_token

        finally:
            await runner.cleanup()

    def _create_callback_app(self, auth_code_future: asyncio.Future) -> web.Application:
        """
        Create aiohttp app for OAuth callback.

        Args:
            auth_code_future: Future to resolve with auth code

        Returns:
            aiohttp Application
        """

        async def callback_handler(request: web.Request) -> web.Response:
            """Handle OAuth callback."""
            # Parse query parameters
            query_params = request.rel_url.query

            # Check for error
            if "error" in query_params:
                error = query_params.get("error", "unknown_error")
                error_desc = query_params.get("error_description", "No description")
                if not auth_code_future.done():
                    auth_code_future.set_exception(
                        RuntimeError(f"OAuth error: {error} - {error_desc}")
                    )
                return web.Response(
                    text=f"<h1>Authentication Failed</h1><p>{html.escape(error_desc)}</p>",
                    content_type="text/html",
                )

            # Extract authorization code
            auth_code = query_params.get("code")
            if not auth_code:
                if not auth_code_future.done():
                    auth_code_future.set_exception(
                        RuntimeError("No authorization code received")
                    )
                return web.Response(
                    text="<h1>Error</h1><p>No authorization code received</p>",
                    content_type="text/html",
                )

            # Resolve future with auth code (avoid race condition)
            if not auth_code_future.done():
                auth_code_future.set_result(auth_code)

            # Return success page
            return web.Response(
                text="""
                <html>
                <head><title>FastApps - Authentication Success</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>✓ Authentication Successful</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """,
                content_type="text/html",
            )

        app = web.Application()
        app.router.add_get("/callback", callback_handler)
        return app

    async def _exchange_code_for_token(
        self, auth_code: str, code_verifier: str
    ) -> str:
        """
        Exchange authorization code for access token.

        Args:
            auth_code: Authorization code from OAuth callback
            code_verifier: PKCE code verifier

        Returns:
            Access token

        Raises:
            RuntimeError: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "code": auth_code,
                        "redirect_uri": self.redirect_uri,
                        "code_verifier": code_verifier,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Token exchange failed: {response.status_code} - {response.text}"
                    )

                token_data = response.json()
                access_token = token_data.get("access_token")

                if not access_token:
                    raise RuntimeError("No access token in response")

                return access_token

            except httpx.ConnectError as e:
                raise ConnectionError(f"Cannot connect to server: {e}")
            except httpx.TimeoutException as e:
                raise TimeoutError(f"Request timed out: {e}")
            except httpx.RequestError as e:
                raise RuntimeError(f"Token exchange request failed: {e}")
