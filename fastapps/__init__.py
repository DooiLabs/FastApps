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

# Get version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("fastapps")
except Exception:
    __version__ = "1.2.0"  # Fallback version

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
] + _auth_exports
