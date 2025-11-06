from fastapps import BaseWidget, ConfigDict
from pydantic import BaseModel
from typing import Dict, Any

# Optional: Add per-widget authentication
# from fastapps import auth_required, no_auth, optional_auth, UserContext


class {ClassName}Input(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


# Optional: Require authentication for this widget
# @auth_required(scopes=["user"])
# Or make it explicitly public:
# @no_auth
# Or support both authenticated and anonymous:
# @optional_auth(scopes=["user"])
class {ClassName}Tool(BaseWidget):
    identifier = "{identifier}"
    title = "{title}"
    input_schema = {ClassName}Input
    invoking = "Loading widget..."
    invoked = "Widget ready!"

    widget_csp = {
        "connect_domains": [],
        "resource_domains": []
    }

    async def execute(self, input_data: {ClassName}Input, context=None, user=None) -> Dict[str, Any]:
        # Access authenticated user (if present)
        # if user and user.is_authenticated:
        #     return {
        #         "message": f"Hello {user.subject}!",
        #         "scopes": user.scopes,
        #         "user_data": user.claims
        #     }

        return {
            "message": "Welcome to FastApps"
        }
