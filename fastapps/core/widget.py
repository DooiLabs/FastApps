from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import mcp.types as types
from pydantic import BaseModel

from fastapps.builder.compiler import WidgetBuildResult


class UserContext:
    """
    Authenticated user context from OAuth token.
    Available in widget execute() when user is authenticated.

    Example:
        async def execute(self, input_data, context, user: UserContext):
            if user.is_authenticated:
                return {"user_id": user.subject, "scopes": user.scopes}
            return {"message": "Anonymous user"}
    """

    def __init__(self, access_token: Optional[Any] = None):
        """
        Initialize user context with access token.

        Args:
            access_token: AccessToken object from OAuth verification (optional)
        """
        self._access_token = access_token

    @property
    def is_authenticated(self) -> bool:
        """Whether user is authenticated"""
        return self._access_token is not None

    @property
    def subject(self) -> Optional[str]:
        """User identifier (sub claim from JWT)"""
        return self._access_token.subject if self._access_token else None

    @property
    def client_id(self) -> Optional[str]:
        """OAuth client ID"""
        return self._access_token.client_id if self._access_token else None

    @property
    def scopes(self) -> List[str]:
        """Granted OAuth scopes"""
        return self._access_token.scopes if self._access_token else []

    @property
    def claims(self) -> Dict[str, Any]:
        """Full JWT claims"""
        return self._access_token.claims if self._access_token else {}

    def has_scope(self, scope: str) -> bool:
        """
        Check if user has specific scope.

        Args:
            scope: Scope to check (e.g., "user", "write:data")

        Returns:
            True if user has the scope, False otherwise
        """
        return scope in self.scopes


class ClientContext:
    """
    Client context information passed to widget execute method.
    Contains metadata about the client environment and user.
    """

    def __init__(self, meta: Dict[str, Any]):
        self._meta = meta

    @property
    def user_agent(self) -> Optional[str]:
        """Client user agent string (e.g., 'ChatGPT/1.2025.012')"""
        return self._meta.get("openai/userAgent")

    @property
    def user_location(self) -> Optional[Dict[str, Any]]:
        """
        Coarse user location information.
        May include: country, region, city, timezone, coordinates.
        """
        return self._meta.get("openai/userLocation")

    @property
    def locale(self) -> Optional[str]:
        """
        User's preferred locale (IETF BCP 47 format).
        Examples: 'en-US', 'fr-FR', 'es-419'
        Falls back to 'webplus/i18n' for older clients.
        """
        return self._meta.get("openai/locale") or self._meta.get("webplus/i18n")

    @property
    def raw_meta(self) -> Dict[str, Any]:
        """Access to raw _meta dictionary"""
        return self._meta


class BaseWidget(ABC):
    """
    Base class for Flick widgets.

    Inherit from this class to create custom ChatGPT widgets.
    """

    identifier: str
    title: str
    input_schema: type[BaseModel]
    description: str = ""
    invoking: str = "Processing..."
    invoked: str = "Completed"

    # OpenAI advanced options
    widget_accessible: bool = True
    widget_description: Optional[str] = None
    widget_csp: Optional[Dict[str, List[str]]] = None
    widget_prefers_border: bool = False
    widget_domain: Optional[str] = None

    # Localization support
    supported_locales: Optional[List[str]] = (
        None  # e.g., ["en", "en-US", "es", "fr-FR"]
    )
    default_locale: str = "en"

    def __init__(self, build_result: WidgetBuildResult):
        self.build_result = build_result
        self.template_uri = f"ui://widget/{self.identifier}.html"
        self.resolved_locale = self.default_locale

    @abstractmethod
    async def execute(
        self,
        input_data: BaseModel,
        context: Optional[ClientContext] = None,
        user: Optional[UserContext] = None,
    ) -> Dict[str, Any]:
        """
        Execute the widget logic and return data for the UI.

        Args:
            input_data: Validated input parameters from ChatGPT
            context: Optional client context with user agent, location, and locale
            user: Optional user context with authenticated user information

        Returns:
            Dictionary of data to pass to the React component

        Example:
            async def execute(self, input_data, context, user):
                if user and user.is_authenticated:
                    return {"message": f"Hello, {user.subject}!"}
                return {"message": "Hello, guest!"}
        """
        pass

    def negotiate_locale(self, requested_locale: Optional[str]) -> str:
        """
        Negotiate locale using RFC 4647 lookup rules.

        Args:
            requested_locale: Client's requested locale (e.g., 'en-US', 'fr-FR')

        Returns:
            Best matching supported locale or default locale
        """
        if not requested_locale or not self.supported_locales:
            return self.default_locale

        # Exact match
        if requested_locale in self.supported_locales:
            return requested_locale

        # Try language-only match (e.g., 'en' for 'en-US')
        language_only = requested_locale.split("-")[0]
        if language_only in self.supported_locales:
            return language_only

        # Try finding any locale with matching language
        for locale in self.supported_locales:
            if locale.startswith(language_only):
                return locale

        return self.default_locale

    def get_input_schema(self) -> Dict[str, Any]:
        """Convert Pydantic model to JSON Schema."""
        return self.input_schema.model_json_schema()

    def get_tool_meta(self) -> Dict[str, Any]:
        """Tool metadata following MCP specification."""
        meta = {
            "openai/outputTemplate": self.template_uri,
            "openai/toolInvocation/invoking": self.invoking,
            "openai/toolInvocation/invoked": self.invoked,
            "openai/widgetAccessible": self.widget_accessible,
            "openai/resultCanProduceWidget": True
        }

        # Add security schemes if defined (per MCP spec)
        if hasattr(self, "_security_schemes"):
            meta["securitySchemes"] = self._security_schemes

        # Add locale if widget supports localization
        if self.resolved_locale:
            meta["openai/locale"] = self.resolved_locale

        return meta

    def get_resource_meta(self) -> Dict[str, Any]:
        """Resource metadata (CSP, border settings, domain, locale)."""
        meta = {}
        if self.widget_csp:
            meta["openai/widgetCSP"] = self.widget_csp
        if self.widget_prefers_border:
            meta["openai/widgetPrefersBorder"] = True
        if self.widget_description:
            meta["openai/widgetDescription"] = self.widget_description
        if self.widget_domain:
            meta["openai/widgetDomain"] = self.widget_domain
        if self.resolved_locale:
            meta["openai/locale"] = self.resolved_locale
        return meta

    def get_embedded_resource(self) -> types.EmbeddedResource:
        """Build embedded resource for tool response."""
        return types.EmbeddedResource(
            type="resource",
            resource=types.TextResourceContents(
                uri=self.template_uri,
                mimeType="text/html+skybridge",
                text=self.build_result.html,
                title=self.title,
                _meta=self.get_resource_meta(),
            ),
        )
