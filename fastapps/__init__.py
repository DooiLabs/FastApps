"""
FastApps - ChatGPT Widget Framework

A zero-boilerplate framework for building interactive ChatGPT widgets.

Example:
    from fastapps import BaseWidget, Field
    from typing import Dict, Any

    class MyWidget(BaseWidget):
        identifier = "my_widget"
        title = "My Widget"

        async def execute(self, input_data) -> Dict[str, Any]:
            return {"message": "Hello from FastApps!"}
"""

__author__ = "FastApps Team"

from .builder.compiler import WidgetBuilder, WidgetBuildResult
from .core.server import WidgetMCPServer
from .core.widget import BaseWidget, ClientContext, UserContext
from .types.schema import ConfigDict, Field

# Auth exports (optional, graceful if not available)
try:
    from .auth import AccessToken, TokenVerifier
    from .auth.decorators import auth_required, no_auth, optional_auth
    from .auth.verifier import JWTVerifier

    _auth_exports = [
        "JWTVerifier",
        "TokenVerifier",
        "AccessToken",
        "auth_required",
        "no_auth",
        "optional_auth",
    ]
except ImportError:
    _auth_exports = []

__all__ = [
    # Core classes
    "BaseWidget",
    "ClientContext",
    "UserContext",
    "WidgetMCPServer",
    "WidgetBuilder",
    "WidgetBuildResult",
    "Field",
    "ConfigDict",
    # Dev server API
    "start_dev_server",
    "start_dev_server_with_config",
    "get_server_info",
    "run_dev_server",
    "DevServerConfig",
    "ServerInfo",
    "DevServerError",
    "ProjectNotFoundError",
] + _auth_exports
