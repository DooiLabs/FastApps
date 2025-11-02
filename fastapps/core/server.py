from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp import types

from fastapps.core.utils import get_cli_version

from .widget import BaseWidget, ClientContext, UserContext


# Auth imports (optional, graceful degradation if not available)
try:
    from mcp.server.auth.provider import TokenVerifier
    from mcp.server.auth.settings import AuthSettings

    MCP_AUTH_AVAILABLE = True
except ImportError:
    MCP_AUTH_AVAILABLE = False
    AuthSettings = None
    TokenVerifier = None


class WidgetMCPServer:
    """
    FastMCP-based MCP server with widget metadata support.

    Handles tool registration, resource templates, and widget execution.
    Supports optional OAuth 2.1 authentication.
    """

    def __init__(
        self,
        name: str,
        widgets: List[BaseWidget],
        # OAuth 2.1 authentication parameters (optional)
        auth_issuer_url: Optional[str] = None,
        auth_resource_server_url: Optional[str] = None,
        auth_required_scopes: Optional[List[str]] = None,
        auth_audience: Optional[str] = None,
        token_verifier: Optional["TokenVerifier"] = None,
    ):
        """
        Initialize MCP server with optional OAuth authentication.

        Args:
            name: Server name
            widgets: List of widget instances
            auth_issuer_url: OAuth issuer URL (e.g., https://tenant.auth0.com)
            auth_resource_server_url: Your MCP server URL (e.g., https://example.com/mcp)
            auth_required_scopes: Required OAuth scopes (e.g., ["user", "read:data"])
            auth_audience: JWT audience claim (optional)
            token_verifier: Custom TokenVerifier (optional, uses JWTVerifier if not provided)

        Example (Simple):
            server = WidgetMCPServer(
                name="my-widgets",
                widgets=tools,
                auth_issuer_url="https://tenant.auth0.com",
                auth_resource_server_url="https://example.com/mcp",
                auth_required_scopes=["user"],
            )

        Example (Custom Verifier):
            server = WidgetMCPServer(
                name="my-widgets",
                widgets=tools,
                auth_issuer_url="https://tenant.auth0.com",
                auth_resource_server_url="https://example.com/mcp",
                token_verifier=MyCustomVerifier(),
            )
        """
        self.widgets_by_id = {w.identifier: w for w in widgets}
        self.widgets_by_uri = {w.template_uri: w for w in widgets}
        self.client_locale: Optional[str] = None

        # Store server auth configuration for per-widget inheritance
        self.server_requires_auth = bool(auth_issuer_url and auth_resource_server_url)
        self.server_auth_scopes = auth_required_scopes or []
        self.token_verifier_instance = None

        # Configure authentication if provided
        auth_settings = None
        verifier = token_verifier

        if auth_issuer_url and auth_resource_server_url:
            if not MCP_AUTH_AVAILABLE:
                raise ImportError(
                    "FastMCP auth support not available. "
                    "Please upgrade fastmcp: pip install --upgrade fastmcp or uv pip install --upgrade fastmcp"
                )

            # Use built-in JWTVerifier if no custom verifier provided
            if verifier is None:
                from ..auth.verifier import JWTVerifier

                verifier = JWTVerifier(
                    issuer_url=auth_issuer_url,
                    audience=auth_audience,
                    required_scopes=auth_required_scopes or [],
                )

            # Create AuthSettings for FastMCP
            auth_settings = AuthSettings(
                issuer_url=auth_issuer_url,
                resource_server_url=auth_resource_server_url,
                required_scopes=auth_required_scopes or [],
            )

            # Store verifier for per-widget validation
            self.token_verifier_instance = verifier

        # Initialize FastMCP with or without auth
        if auth_settings:
            self.mcp = FastMCP(
                name=name,
                stateless_http=True,
                token_verifier=verifier,
                auth=auth_settings,
            )
        else:
            self.mcp = FastMCP(name=name)

        self._register_handlers()

    def _register_handlers(self):
        """Register all MCP handlers for widget support."""
        server = self.mcp._mcp_server

        # Handle MCP initialization to negotiate locale
        original_initialize = server.request_handlers.get(types.InitializeRequest)

        async def initialize_handler(
            req: types.InitializeRequest,
        ) -> types.ServerResult:
            # Extract requested locale from _meta
            meta = req.params._meta if hasattr(req.params, "_meta") else {}
            requested_locale = meta.get("openai/locale") or meta.get("webplus/i18n")

            # Negotiate locale with each widget
            if requested_locale:
                self.client_locale = requested_locale
                for widget in self.widgets_by_id.values():
                    resolved = widget.negotiate_locale(requested_locale)
                    widget.resolved_locale = resolved

            # Call original handler if it exists
            if original_initialize:
                return await original_initialize(req)

            # Default response if no original handler
            return types.ServerResult(
                types.InitializeResult(
                    protocolVersion=req.params.protocolVersion,
                    capabilities=types.ServerCapabilities(),
                    serverInfo=types.Implementation(name="FastApps", version=get_cli_version()),
                )
            )

        server.request_handlers[types.InitializeRequest] = initialize_handler

        @server.list_tools()
        async def list_tools_handler() -> List[types.Tool]:
            tools_list = []
            for w in self.widgets_by_id.values():
                tool_meta = w.get_tool_meta()

                # Per MCP spec: "Missing field: inherit server default policy"
                # If widget doesn't have explicit securitySchemes and server has auth,
                # inherit server's auth requirement
                if "securitySchemes" not in tool_meta and self.server_requires_auth:
                    tool_meta["securitySchemes"] = [
                        {"type": "oauth2", "scopes": self.server_auth_scopes}
                    ]

                tools_list.append(
                    types.Tool(
                        name=w.identifier,
                        title=w.title,
                        description=w.description or w.title,
                        inputSchema=w.get_input_schema(),
                        _meta=tool_meta,
                    )
                )
            return tools_list

        @server.list_resources()
        async def list_resources_handler() -> List[types.Resource]:
            return [
                types.Resource(
                    name=w.title,
                    title=w.title,
                    uri=w.template_uri,
                    description=f"{w.title} widget markup",
                    mimeType="text/html+skybridge",
                    _meta=w.get_resource_meta(),
                )
                for w in self.widgets_by_id.values()
            ]

        @server.list_resource_templates()
        async def list_resource_templates_handler() -> List[types.ResourceTemplate]:
            return [
                types.ResourceTemplate(
                    name=w.title,
                    title=w.title,
                    uriTemplate=w.template_uri,
                    description=f"{w.title} widget markup",
                    mimeType="text/html+skybridge",
                    _meta=w.get_resource_meta(),
                )
                for w in self.widgets_by_id.values()
            ]

        async def read_resource_handler(
            req: types.ReadResourceRequest,
        ) -> types.ServerResult:
            widget = self.widgets_by_uri.get(str(req.params.uri))
            if not widget:
                return types.ServerResult(
                    types.ReadResourceResult(
                        contents=[],
                        _meta={"error": f"Unknown resource: {req.params.uri}"},
                    )
                )

            contents = [
                types.TextResourceContents(
                    uri=widget.template_uri,
                    mimeType="text/html+skybridge",
                    text=widget.build_result.html,
                    _meta=widget.get_resource_meta(),
                )
            ]
            return types.ServerResult(types.ReadResourceResult(contents=contents))

        async def call_tool_handler(req: types.CallToolRequest) -> types.ServerResult:
            widget = self.widgets_by_id.get(req.params.name)
            if not widget:
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text", text=f"Unknown tool: {req.params.name}"
                            )
                        ],
                        isError=True,
                    )
                )

            try:
                # Extract verified access token
                # FastMCP verifies token before this handler if auth is enabled
                access_token = None
                if hasattr(req, "context") and hasattr(req.context, "access_token"):
                    access_token = req.context.access_token
                elif hasattr(req.params, "_meta"):
                    # Fallback: check _meta for token info
                    meta_token = req.params._meta.get("access_token")
                    if meta_token:
                        access_token = meta_token

                # Determine if auth is required for this widget
                widget_requires_auth = getattr(widget, "_auth_required", None)

                # Per MCP spec: Inheritance - widget without decorator inherits server policy
                if widget_requires_auth is None and self.server_requires_auth:
                    widget_requires_auth = True

                # Per MCP spec: "Servers must enforce regardless of client hints"
                if widget_requires_auth is True and not access_token:
                    return types.ServerResult(
                        types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text="Authentication required for this tool",
                                )
                            ],
                            isError=True,
                        )
                    )

                # Enforce widget-specific scope requirements
                if (
                    access_token
                    and hasattr(widget, "_auth_scopes")
                    and widget._auth_scopes
                ):
                    user_scopes = getattr(access_token, "scopes", [])
                    missing_scopes = set(widget._auth_scopes) - set(user_scopes)

                    if missing_scopes:
                        return types.ServerResult(
                            types.CallToolResult(
                                content=[
                                    types.TextContent(
                                        type="text",
                                        text=f"Missing required scopes: {', '.join(missing_scopes)}",
                                    )
                                ],
                                isError=True,
                            )
                        )

                # Validate input
                arguments = req.params.arguments or {}
                input_data = widget.input_schema.model_validate(arguments)

                # Extract client context from request metadata
                meta = req.params._meta if hasattr(req.params, "_meta") else {}

                # Re-negotiate locale if provided in this request
                requested_locale = meta.get("openai/locale") or meta.get("webplus/i18n")
                if requested_locale:
                    widget.resolved_locale = widget.negotiate_locale(requested_locale)

                # Create contexts
                context = ClientContext(meta)
                user = UserContext(access_token)

                # Call execute with user context
                result_data = await widget.execute(input_data, context, user)
            except Exception as exc:
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(type="text", text=f"Error: {str(exc)}")
                        ],
                        isError=True,
                    )
                )

            widget_resource = widget.get_embedded_resource()
            meta: Dict[str, Any] = {
                "openai.com/widget": widget_resource.model_dump(mode="json"),
                "openai/outputTemplate": widget.template_uri,
                "openai/toolInvocation/invoking": widget.invoking,
                "openai/toolInvocation/invoked": widget.invoked,
                "openai/widgetAccessible": widget.widget_accessible,
                "openai/resultCanProduceWidget": True,
            }

            # Add resolved locale to response
            if widget.resolved_locale:
                meta["openai/locale"] = widget.resolved_locale

            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=widget.invoked)],
                    structuredContent=result_data,
                    _meta=meta,
                )
            )

        server.request_handlers[types.ReadResourceRequest] = read_resource_handler
        server.request_handlers[types.CallToolRequest] = call_tool_handler

    def get_app(self):
        """Get FastAPI app with CORS enabled."""
        app = self.mcp.http_app()

        try:
            from starlette.middleware.cors import CORSMiddleware

            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                allow_credentials=False,
            )
        except Exception:
            pass

        return app
