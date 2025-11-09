# OAuth Testing Guide for FastApps

Complete guide to test per-widget authentication with real OAuth flow.

## Prerequisites

- Python 3.11+
- Node.js 18+
- ngrok account (free tier works)
- Auth0 or Okta account (free tier works)

## Part 1: Set Up Auth0

### Step 1: Create Auth0 Account

1. Go to https://auth0.com/signup
2. Create a free account
3. Note your domain: `YOUR_TENANT.us.auth0.com`

### Step 2: Create an API

1. Dashboard → Applications → APIs
2. Click "Create API"
3. Fill in:
   - **Name**: FastApps Test API
   - **Identifier**: `https://fastapps-test.example.com` (can be any URL)
   - **Signing Algorithm**: RS256
4. Click "Create"
5. **Save the Identifier** - you'll need it as `auth_audience`

### Step 3: Add Permissions (Scopes)

1. In your API → Permissions tab
2. Add these permissions:
   - `user` - Basic user access
   - `read:data` - Read data permission
   - `write:data` - Write data permission
   - `admin` - Admin access

### Step 4: Enable RBAC

1. In your API → Settings tab
2. Scroll to "RBAC Settings"
3. Toggle ON: **Enable RBAC**
4. Toggle ON: **Add Permissions in the Access Token**
5. Click "Save"

### Step 5: Enable Dynamic Client Registration

1. Dashboard → Settings (gear icon in left sidebar)
2. Scroll to "API Authorization Settings"
3. Find "Dynamic Client Registration"
4. Toggle ON: **OIDC Dynamic Application Registration**
5. Click "Save"

### Step 6: Create a User (for testing)

1. Dashboard → User Management → Users
2. Click "Create User"
3. Fill in email and password
4. After creation, click on the user
5. Go to "Permissions" tab
6. Click "Assign Permissions"
7. Select your API and assign all permissions
8. Click "Add Permissions"

### Step 7: Get Your Configuration

You'll need these values:
```
ISSUER_URL: https://YOUR_TENANT.us.auth0.com
RESOURCE_SERVER_URL: https://YOUR_NGROK_URL.ngrok-free.app/mcp
AUDIENCE: https://fastapps-test.example.com (from Step 2)
```

---

## Part 2: Create Test Project

### Step 1: Initialize Project

```bash
cd /Users/yunhyeok/Desktop/fastapps
mkdir auth-test
cd auth-test

# Create venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastApps
uv pip install -e ../FastApps

# Install dependencies
uv pip install httpx PyJWT cryptography

# Initialize project
uv run fastapps init auth-test-project
cd auth-test-project

# Install JS dependencies
npm install
```

### Step 2: Create Test Widgets

Create three test widgets to test all decorator types:

#### 1. Protected Widget (auth required)

```bash
uv run fastapps create protected-widget
```

Edit `server/tools/protected_widget_tool.py`:
```python
from fastapps import BaseWidget, ConfigDict, auth_required, UserContext
from pydantic import BaseModel
from typing import Dict, Any

class ProtectedWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    message: str = "Hello"

@auth_required(scopes=["user", "read:data"])
class ProtectedWidgetTool(BaseWidget):
    identifier = "protected-widget"
    title = "Protected Widget"
    description = "This widget requires authentication with user and read:data scopes"
    input_schema = ProtectedWidgetInput
    invoking = "Loading protected widget..."
    invoked = "Protected widget loaded!"
    
    widget_csp = {
        "connect_domains": [],
        "resource_domains": []
    }
    
    async def execute(self, input_data: ProtectedWidgetInput, context=None, user: UserContext = None) -> Dict[str, Any]:
        if not user or not user.is_authenticated:
            return {"error": "This should never happen - auth is required"}
        
        return {
            "message": f"Hello, {user.claims.get('name', 'User')}!",
            "user_id": user.subject,
            "email": user.claims.get('email', 'N/A'),
            "scopes": user.scopes,
            "has_read": user.has_scope("read:data"),
            "has_write": user.has_scope("write:data"),
            "has_admin": user.has_scope("admin"),
            "input_message": input_data.message,
        }
```

#### 2. Public Widget (no auth)

```bash
uv run fastapps create public-widget
```

Edit `server/tools/public_widget_tool.py`:
```python
from fastapps import BaseWidget, ConfigDict, no_auth
from pydantic import BaseModel
from typing import Dict, Any

class PublicWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

@no_auth
class PublicWidgetTool(BaseWidget):
    identifier = "public-widget"
    title = "Public Widget"
    description = "This widget is public - no authentication required"
    input_schema = PublicWidgetInput
    invoking = "Loading public widget..."
    invoked = "Public widget loaded!"
    
    widget_csp = {
        "connect_domains": [],
        "resource_domains": []
    }
    
    async def execute(self, input_data: PublicWidgetInput, context=None, user=None) -> Dict[str, Any]:
        return {
            "message": "This is public content",
            "authenticated": user.is_authenticated if user else False,
            "note": "Anyone can access this widget"
        }
```

#### 3. Flexible Widget (optional auth)

```bash
uv run fastapps create flexible-widget
```

Edit `server/tools/flexible_widget_tool.py`:
```python
from fastapps import BaseWidget, ConfigDict, optional_auth, UserContext
from pydantic import BaseModel
from typing import Dict, Any

class FlexibleWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

@optional_auth(scopes=["user"])
class FlexibleWidgetTool(BaseWidget):
    identifier = "flexible-widget"
    title = "Flexible Widget"
    description = "This widget works for both authenticated and anonymous users"
    input_schema = FlexibleWidgetInput
    invoking = "Loading flexible widget..."
    invoked = "Flexible widget loaded!"
    
    widget_csp = {
        "connect_domains": [],
        "resource_domains": []
    }
    
    async def execute(self, input_data: FlexibleWidgetInput, context=None, user: UserContext = None) -> Dict[str, Any]:
        if user and user.is_authenticated:
            # Premium features for authenticated users
            return {
                "tier": "premium",
                "message": f"Welcome back, {user.claims.get('name', 'User')}!",
                "user_id": user.subject,
                "features": ["basic", "advanced", "export", "share"],
                "personalized": True,
            }
        
        # Basic features for anonymous users
        return {
            "tier": "free",
            "message": "Welcome! Sign in to unlock premium features.",
            "features": ["basic"],
            "personalized": False,
        }
```

### Step 3: Update Server Configuration

Edit `server/main.py` to enable OAuth:

```python
from pathlib import Path
import sys
import importlib
import inspect

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapps import WidgetBuilder, WidgetMCPServer, BaseWidget
import uvicorn

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent / "tools"

def auto_load_tools(build_results):
    """Automatically discover and load all widget tools."""
    tools = []
    for tool_file in TOOLS_DIR.glob("*_tool.py"):
        module_name = tool_file.stem
        try:
            module = importlib.import_module(f"server.tools.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseWidget) and obj is not BaseWidget:
                    tool_identifier = obj.identifier
                    if tool_identifier in build_results:
                        tool_instance = obj(build_results[tool_identifier])
                        tools.append(tool_instance)
                        print(f"✓ Loaded tool: {name} (identifier: {tool_identifier})")
                    else:
                        print(f"⚠ Warning: No build result found for tool '{tool_identifier}'")
        except Exception as e:
            print(f"✗ Error loading {tool_file.name}: {e}")
    return tools

# Build all widgets
builder = WidgetBuilder(PROJECT_ROOT)
build_results = builder.build_all()

# Auto-load and register tools
tools = auto_load_tools(build_results)

# IMPORTANT: Replace these with your Auth0 values
AUTH0_DOMAIN = "YOUR_TENANT.us.auth0.com"  # Replace with your Auth0 domain
AUTH0_AUDIENCE = "https://fastapps-test.example.com"  # Replace with your API identifier
NGROK_URL = "https://YOUR_URL.ngrok-free.app"  # You'll get this after starting ngrok

# Create MCP server WITH authentication
server = WidgetMCPServer(
    name="fastapps-auth-test",
    widgets=tools,
    # OAuth configuration
    auth_issuer_url=f"https://{AUTH0_DOMAIN}",
    auth_resource_server_url=f"{NGROK_URL}/mcp",
    auth_audience=AUTH0_AUDIENCE,
    auth_required_scopes=["user"],  # Default scope for widgets without decorators
)

app = server.get_app()

if __name__ == "__main__":
    print(f"\n🚀 Starting FastApps Test Server with OAuth")
    print(f"   Auth Provider: {AUTH0_DOMAIN}")
    print(f"   Widgets: {len(tools)}")
    print(f"   Port: 8001")
    print(f"\n⚠️  Remember to start ngrok in another terminal:")
    print(f"   ngrok http 8001")
    print(f"\n📝 After getting ngrok URL, update NGROK_URL in this file")
    print(f"\n✨ Test widgets:")
    for tool in tools:
        auth_status = "🔒 AUTH REQUIRED" if getattr(tool, '_auth_required', None) is True else \
                     "🌐 PUBLIC" if getattr(tool, '_auth_required', None) is False else \
                     "🔓 OPTIONAL AUTH"
        print(f"   - {tool.title}: {auth_status}")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## Part 3: Build and Run

### Step 1: Build Widgets

```bash
npm run build
```

You should see:
```
Found widget: protected-widget
Found widget: public-widget
Found widget: flexible-widget

Ready to build 3 widget(s)
```

### Step 2: Start Server (Terminal 1)

```bash
python server/main.py
```

You should see:
```
🚀 Starting FastApps Test Server with OAuth
   Auth Provider: YOUR_TENANT.us.auth0.com
   Widgets: 3
   Port: 8001
   
⚠️  Remember to start ngrok in another terminal:
   ngrok http 8001
```

### Step 3: Start ngrok (Terminal 2)

```bash
ngrok http 8001
```

You'll get output like:
```
Session Status                online
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8001
```

**IMPORTANT**: Copy the `https://...ngrok-free.app` URL!

### Step 4: Update Server with ngrok URL

1. Stop the server (Ctrl+C in Terminal 1)
2. Edit `server/main.py`
3. Update `NGROK_URL = "https://abc123.ngrok-free.app"` with your actual URL
4. Restart server: `python server/main.py`

---

## Part 4: Test with ChatGPT

### Step 1: Add Connector to ChatGPT

1. Open ChatGPT
2. Go to Settings (gear icon)
3. Click "Connectors"
4. Click "Add Connector"
5. Enter your ngrok URL with `/mcp` path:
   ```
   https://abc123.ngrok-free.app/mcp
   ```
6. Click "Add"

### Step 2: Authenticate

ChatGPT will prompt you to authenticate:
1. Click "Authenticate"
2. You'll be redirected to Auth0
3. Log in with the test user you created
4. Grant permissions
5. You'll be redirected back to ChatGPT

### Step 3: Test Widgets

Try these commands in ChatGPT:

**Test 1: Protected Widget (should require auth)**
```
Use the protected-widget tool with message "Testing auth"
```

Expected response:
- Shows your user info
- Shows your scopes
- Works because you're authenticated

**Test 2: Public Widget (works without auth)**
```
Use the public-widget tool
```

Expected response:
- Works immediately
- Shows authenticated status
- No auth prompt

**Test 3: Flexible Widget (works both ways)**
```
Use the flexible-widget tool
```

Expected response (authenticated):
- Shows "premium" tier
- Shows personalized features
- Shows your user info

Try this in an incognito/private window (unauthenticated):
- Should show "free" tier
- Shows basic features only

---

## Part 5: Verify Implementation

### Check 1: Security Schemes in Tool List

You can verify the securitySchemes are set correctly:

```bash
curl http://localhost:8001/mcp/tools
```

Look for:
```json
{
  "tools": [
    {
      "name": "protected-widget",
      "_meta": {
        "securitySchemes": [
          {"type": "oauth2", "scopes": ["user", "read:data"]}
        ]
      }
    },
    {
      "name": "public-widget",
      "_meta": {
        "securitySchemes": [
          {"type": "noauth"}
        ]
      }
    },
    {
      "name": "flexible-widget",
      "_meta": {
        "securitySchemes": [
          {"type": "noauth"},
          {"type": "oauth2", "scopes": ["user"]}
        ]
      }
    }
  ]
}
```

### Check 2: OAuth Discovery

```bash
curl http://localhost:8001/.well-known/oauth-protected-resource
```

Should return Auth0 configuration.

### Check 3: Server Logs

Watch terminal for:
- `✓ Loaded tool: ProtectedWidgetTool (identifier: protected-widget)`
- `✓ Loaded tool: PublicWidgetTool (identifier: public-widget)`
- `✓ Loaded tool: FlexibleWidgetTool (identifier: flexible-widget)`

---

## Troubleshooting

### Issue: "Authentication required" error

**Cause**: Token not present or invalid

**Solution**:
1. Make sure you authenticated in ChatGPT
2. Check Auth0 user has permissions assigned
3. Verify `auth_audience` matches API identifier
4. Check `auth_issuer_url` is correct

### Issue: "Missing required scopes"

**Cause**: User doesn't have the required scopes

**Solution**:
1. Go to Auth0 Dashboard → Users
2. Click on your test user
3. Go to Permissions tab
4. Assign missing permissions

### Issue: ngrok URL changed

**Cause**: ngrok generates new URL on restart (free tier)

**Solution**:
1. Get new ngrok URL
2. Update `NGROK_URL` in `server/main.py`
3. Restart server
4. Update connector URL in ChatGPT

### Issue: Widget not found

**Cause**: Build issue or widget not loaded

**Solution**:
```bash
# Rebuild
npm run build

# Check build output
ls assets/

# Should see:
# protected-widget-XXXX.html
# public-widget-XXXX.html
# flexible-widget-XXXX.html
```

---

## Expected Behavior Summary

| Widget | Decorator | Anonymous Access | Authenticated Access |
|--------|-----------|-----------------|---------------------|
| Protected | `@auth_required` | ❌ Error | ✅ Works, shows user info |
| Public | `@no_auth` | ✅ Works | ✅ Works, notes auth status |
| Flexible | `@optional_auth` | ✅ Basic features | ✅ Premium features |

---

## Next Steps

After successful testing:

1. **Add more scopes**: Test with `admin` scope
2. **Test scope enforcement**: Remove scopes from user, verify errors
3. **Test inheritance**: Create widget without decorator, verify inherits server auth
4. **Test error handling**: Try invalid tokens, expired tokens
5. **Production deployment**: Use real domain instead of ngrok

---

## Clean Up

When done testing:

```bash
# Stop server (Terminal 1): Ctrl+C
# Stop ngrok (Terminal 2): Ctrl+C

# Deactivate venv
deactivate

# Remove test project (optional)
cd /Users/yunhyeok/Desktop/fastapps
rm -rf auth-test
```

---

**Need help?** Check:
- Auth0 Logs: Dashboard → Monitoring → Logs
- Server logs: Terminal 1
- ChatGPT connector status: Settings → Connectors
- FastApps docs: `/docs/08-AUTH.md` and `/docs/09-PER-WIDGET-AUTH.md`
