# FastApps OAuth Testing - Quick Summary

## What Was Created

### 1. Comprehensive Testing Guide
**File**: `OAUTH_TESTING_GUIDE.md`

Complete step-by-step guide covering:
- Auth0 setup (with screenshots guidance)
- Project creation
- Three test widgets (protected, public, flexible)
- Server configuration
- ngrok setup
- ChatGPT integration
- Troubleshooting

### 2. Quick Setup Script
**File**: `create_auth_test.sh`

Automated setup script that:
- Creates test project
- Sets up virtual environment
- Installs all dependencies
- Creates three test widgets automatically
- Configures server with your Auth0 credentials
- Builds widgets
- Provides next-steps instructions

## Quick Start (2 Options)

### Option A: Automated Setup (Recommended)

```bash
cd /Users/yunhyeok/Desktop/fastapps/FastApps

# Run the setup script
./create_auth_test.sh

# Follow the prompts:
# - Enter your Auth0 domain
# - Enter your API identifier

# Then follow the printed instructions
```

The script will create everything and give you next steps.

### Option B: Manual Setup

Follow the detailed guide in `OAUTH_TESTING_GUIDE.md` for complete control.

## Test Widgets Overview

### 1. Protected Widget 🔒
**Decorator**: `@auth_required(scopes=["user", "read:data"])`

**Behavior**:
- Requires authentication
- Requires specific scopes
- Shows user information
- ChatGPT will prompt for login

**Test Command**:
```
Use the protected-widget tool with message "Testing auth"
```

**Expected Response**:
```json
{
  "type": "protected",
  "message": "Hello, John Doe!",
  "user_id": "auth0|123456",
  "email": "test@example.com",
  "scopes": ["user", "read:data", "write:data"],
  "permissions": {
    "read": true,
    "write": true,
    "admin": false
  }
}
```

### 2. Public Widget 🌐
**Decorator**: `@no_auth`

**Behavior**:
- No authentication required
- Works immediately
- Shows auth status

**Test Command**:
```
Use the public-widget tool
```

**Expected Response**:
```json
{
  "type": "public",
  "message": "This is public content - no auth required",
  "authenticated": true,
  "access_level": "public"
}
```

### 3. Flexible Widget 🔓
**Decorator**: `@optional_auth(scopes=["user"])`

**Behavior**:
- Works both authenticated and anonymous
- Different features based on auth status
- Perfect for freemium models

**Test Command** (authenticated):
```
Use the flexible-widget tool
```

**Expected Response** (authenticated):
```json
{
  "type": "flexible",
  "tier": "premium",
  "message": "Welcome back, John Doe!",
  "user_id": "auth0|123456",
  "features": ["basic", "advanced", "export", "share"],
  "personalized": true
}
```

**Expected Response** (anonymous):
```json
{
  "type": "flexible",
  "tier": "free",
  "message": "Welcome! Sign in to unlock premium features.",
  "features": ["basic"],
  "personalized": false
}
```

## What to Verify

### ✅ Security Schemes Metadata

Check that widgets have correct `securitySchemes`:

```bash
curl http://localhost:8001/mcp/tools | jq '.tools[] | {name, securitySchemes: ._meta.securitySchemes}'
```

Expected:
```json
{
  "name": "protected-widget",
  "securitySchemes": [
    {"type": "oauth2", "scopes": ["user", "read:data"]}
  ]
}

{
  "name": "public-widget",
  "securitySchemes": [
    {"type": "noauth"}
  ]
}

{
  "name": "flexible-widget",
  "securitySchemes": [
    {"type": "noauth"},
    {"type": "oauth2", "scopes": ["user"]}
  ]
}
```

### ✅ OAuth Discovery

```bash
curl http://localhost:8001/.well-known/oauth-protected-resource
```

Should return Auth0 configuration with:
- Authorization server URL
- Required scopes
- Token endpoint

### ✅ Authentication Flow

1. **Protected widget without auth** → Error
2. **Protected widget with auth** → Success + user data
3. **Public widget** → Always works
4. **Flexible widget** → Different response based on auth

### ✅ Scope Enforcement

Test with user missing required scopes:
1. Remove "read:data" permission from Auth0 user
2. Try protected widget
3. Should get "Missing required scopes" error

## Architecture Verification

The implementation follows MCP specification:

```
ChatGPT
   ↓ (1) List tools
   ↓
FastApps Server
   ↓ Returns tools with securitySchemes metadata
   ↓
ChatGPT sees:
   - protected-widget: requires oauth2
   - public-widget: noauth
   - flexible-widget: both types

When user invokes protected-widget:
   ↓ (2) ChatGPT starts OAuth flow
   ↓ (3) User authenticates with Auth0
   ↓ (4) ChatGPT gets access token
   ↓ (5) Calls tool with token
   ↓
FastApps Server:
   - Extracts token
   - Validates with Auth0 JWKS
   - Checks widget requirements
   - Creates UserContext
   - Calls widget.execute(data, context, user)
   ↓
Widget receives UserContext:
   - user.is_authenticated = True
   - user.subject = "auth0|123456"
   - user.scopes = ["user", "read:data"]
   - user.claims = {full JWT}
```

## Common Issues & Solutions

### Issue: "Module 'mcp.server.auth' not found"

**Cause**: FastMCP version doesn't have auth support

**Solution**:
```bash
uv pip install --upgrade fastmcp
```

### Issue: "Failed to initialize JWKS"

**Cause**: Can't reach Auth0

**Solution**:
1. Check internet connection
2. Verify Auth0 domain is correct
3. Check firewall isn't blocking

### Issue: "Authentication required" in ChatGPT

**Cause**: User not authenticated

**Solution**:
1. Click "Authenticate" button in ChatGPT
2. Log in with test user
3. Grant permissions

### Issue: Widget shows "user is None"

**Cause**: Token not being passed or extracted

**Solution**:
1. Check FastMCP version (needs auth support)
2. Verify token extraction in server.py
3. Check server logs for errors

## Success Criteria

Your implementation is working correctly if:

✅ **Server starts** without errors
✅ **Widgets load** (3 widgets shown in server output)
✅ **Security schemes** are in tool metadata
✅ **Protected widget** requires authentication
✅ **Public widget** works without authentication
✅ **Flexible widget** changes behavior based on auth
✅ **Scope enforcement** works (try removing scopes)
✅ **User context** contains correct user info
✅ **ChatGPT** prompts for authentication when needed

## Performance Metrics

Expected performance:
- **Server startup**: < 5 seconds
- **Widget build**: < 10 seconds (3 widgets)
- **OAuth flow**: < 3 seconds (after user authenticates)
- **Tool invocation**: < 100ms
- **Token verification**: < 50ms (JWKS cached)

## Next Steps After Testing

Once testing is successful:

1. **Production setup**:
   - Use real domain (not ngrok)
   - Configure proper SSL certificates
   - Set up Auth0 production tenant

2. **Add more widgets**:
   - Role-based access widgets
   - Multi-tier feature widgets
   - Admin-only widgets

3. **Enhance security**:
   - Add rate limiting
   - Implement token refresh
   - Add audit logging

4. **Monitor**:
   - Track authentication failures
   - Monitor token validation performance
   - Log unauthorized access attempts

## Documentation Reference

- **Full testing guide**: `OAUTH_TESTING_GUIDE.md`
- **Server-wide auth**: `docs/08-AUTH.md`
- **Per-widget auth**: `docs/09-PER-WIDGET-AUTH.md`
- **Implementation summary**: `PER_WIDGET_AUTH_SUMMARY.md`

## Support

If you encounter issues:

1. Check server logs
2. Check Auth0 logs (Dashboard → Monitoring → Logs)
3. Verify all configurations match
4. Review troubleshooting section in guides
5. Check FastApps GitHub issues

---

**Ready to test?**

```bash
cd /Users/yunhyeok/Desktop/fastapps/FastApps
./create_auth_test.sh
```

Follow the prompts and you'll have a working OAuth test environment in minutes!
