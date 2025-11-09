# ngrok Integration Guide

FastApps now includes built-in ngrok integration for easy development server access!

## What's New

The `uv run fastapps dev` command now:
- ✅ Automatically creates a public ngrok tunnel
- ✅ Manages your ngrok auth token securely
- ✅ Displays both local and public URLs
- ✅ Shows MCP server endpoints
- ✅ Supports custom port and host configuration

## Installation

1. **Install dependencies:**
   ```bash
   uv sync --dev
   ```
   This will install pyngrok and all other required dependencies.

2. **Get ngrok auth token:**
   - Visit https://dashboard.ngrok.com/get-started/your-authtoken
   - Sign up for a free account if you don't have one
   - Copy your auth token

## Usage

### Basic Usage

Start the development server with ngrok:
```bash
uv run fastapps dev
```

On first run, you'll be prompted for your ngrok auth token:
```
ngrok authentication required
Get your free auth token at: https://dashboard.ngrok.com/get-started/your-authtoken

Enter your ngrok auth token: [paste your token here]
✓ Token saved successfully
```

The token is saved in `~/.fastapps/config.json` and won't be requested again.

### Output

After starting, you'll see:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🚀 FastApps Development Server    ┃
┣━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┫
┃ Type       ┃ URL                ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Local      │ http://0.0.0.0:8001│
│ Public     │ https://xyz.ngrok.io│
└────────────┴────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📡 Model Context Protocol         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ MCP Server Endpoint:              ┃
┃ https://xyz.ngrok.io              ┃
┃                                   ┃
┃ Use this URL in your MCP client  ┃
┃ configuration                     ┃
└━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘
```

### Custom Port and Host

Specify custom port:
```bash
uv run fastapps dev --port 8080
```

Specify custom host:
```bash
uv run fastapps dev --host 127.0.0.1 --port 9000
```

View help:
```bash
uv run fastapps dev --help
```

## Managing ngrok Token

### Reset Token

If you want to change your ngrok token:
```bash
uv run fastapps reset-token
```

This will clear the stored token. The next time you run `uv run fastapps dev`, you'll be prompted for a new token.

### Manual Configuration

Alternatively, you can manually edit `~/.fastapps/config.json`:
```json
{
  "ngrok_token": "your_new_token_here"
}
```

## Troubleshooting

### "pyngrok not installed" Error

Install pyngrok:
```bash
uv pip install pyngrok
```

Or reinstall FastApps with all dependencies:
```bash
uv sync --dev
```

### "Not in a FastApps project directory" Error

Make sure you run `uv run fastapps dev` from your project root directory (where `server/main.py` exists).

If you haven't initialized a project yet:
```bash
uv run fastapps init myproject
cd myproject
uv sync
# Or: uv sync --dev (installs dev extras)
npm install
uv run fastapps create mywidget
npm run build
uv run fastapps dev
```

### ngrok Connection Issues

1. **Check your auth token** - Make sure it's valid at https://dashboard.ngrok.com
2. **Reset token** - Run `uv run fastapps reset-token` and try again
3. **Check firewall** - Ensure your firewall allows ngrok connections
4. **Free account limits** - Free ngrok accounts have connection limits

### Port Already in Use

If port 8001 is already in use:
```bash
uv run fastapps dev --port 8002
```

## How It Works

1. **Token Management**: Your ngrok auth token is stored securely in `~/.fastapps/config.json`
2. **Tunnel Creation**: pyngrok creates an HTTPS tunnel to your local server
3. **Server Launch**: uvicorn starts your FastApps server
4. **URL Display**: Both local and public URLs are displayed for easy access

## Benefits

- 🌐 **Public Access**: Share your development server instantly
- 🔒 **HTTPS**: Automatic HTTPS for your development server
- 🎯 **MCP Compatible**: Perfect for testing with ChatGPT and other MCP clients
- 💾 **Persistent Token**: Set once, use forever
- ⚡ **Fast Setup**: From zero to public server in seconds

## Commands Reference

| Command | Description |
|---------|-------------|
| `uv run fastapps dev` | Start dev server with ngrok tunnel |
| `uv run fastapps dev --port 8080` | Start on custom port |
| `uv run fastapps dev --host 127.0.0.1` | Start on custom host |
| `uv run fastapps reset-token` | Clear stored ngrok token |
| `uv run fastapps dev --help` | Show help for dev command |

## Security Notes

- Your ngrok auth token is stored in `~/.fastapps/config.json`
- This file is in your home directory and not part of your project
- Keep your token private and don't commit it to version control
- The `.fastapps` directory is automatically excluded from git

## Next Steps

After starting your dev server:

1. **Test locally**: Visit `http://localhost:8001`
2. **Test publicly**: Visit the ngrok URL (e.g., `https://xyz.ngrok.io`)
3. **Configure MCP client**: Use the ngrok URL as your MCP server endpoint
4. **Test with ChatGPT**: Add your server to ChatGPT's custom actions

## Additional Resources

- **ngrok Documentation**: https://ngrok.com/docs
- **FastApps Documentation**: See `docs/` directory
- **MCP Specification**: https://modelcontextprotocol.io
- **Get ngrok Token**: https://dashboard.ngrok.com/get-started/your-authtoken

## Feedback

If you encounter issues or have suggestions for the ngrok integration, please open an issue on the FastApps GitHub repository.

Happy developing! 🚀
