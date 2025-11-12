# FastApps
<img src="https://github.com/user-attachments/assets/c8766217-427f-4566-8dcb-480f8db12352" width="100%" />

<p align="center">
  <strong>The python framework for apps in ChatGPT</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/v/fastapps.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/pyversions/fastapps.svg" alt="Python"></a>
  <a href="https://pepy.tech/projects/fastapps"><img src="https://static.pepy.tech/personalized-badge/fastapps?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads"></a>
  <a href="https://github.com/DooiLabs/FastApps/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <br>
  <a href="https://github.com/DooiLabs/FastApps/actions"><img src="https://github.com/DooiLabs/FastApps/workflows/CI/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/DooiLabs/FastApps"><img src="https://img.shields.io/github/stars/DooiLabs/FastApps?style=social" alt="GitHub Stars"></a>
</p>

---

📚 **Documentation**: [https://docs.fastapps.org/](https://docs.fastapps.org/)

👥 **Community**: [Join Our Discord](https://discord.gg/5cEy3Jqek3)

---

## Quick Start

We recommend installing FastApps with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install fastapps
uv tool install --upgrade fastapps # Update to the latest version
```

For full installation instructions, including verification, upgrading from the official MCPSDK, and developer setup, see the Installation Guide.

Then, you can quickstart by running commands below :

```bash
uv run fastapps init my-app
cd my-app
npm install
uv sync          # Install Python deps & create uv.lock
uv run fastapps dev
```

That's it! You'll gonna see an image with a public url. You can test the server with following guides.

![alt text](image.png)

The public url is one-time, generated with [cloudflare tunnel](https://github.com/cloudflare/cloudflared).


## Managing Dependencies with uv

FastApps projects now rely on `pyproject.toml` + `uv.lock` for Python dependencies.

- `uv sync` installs everything defined in `pyproject.toml` and writes/updates `uv.lock` for reproducible builds. Run it whenever you pull new changes or after editing dependencies.
- `uv add <package>` adds new dependencies and immediately updates both `pyproject.toml` and `uv.lock`.
- `uv run <command>` executes CLI tools (like `fastapps dev`) inside the synced environment without activating a virtualenv manually.

> **Tip:** If `uv` is not installed, follow their [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) and rerun `uv sync`. Without `uv`, FastApps commands that manage dependencies (e.g., `fastapps init`, `fastapps use`) will fail with a helpful error message.


## Test App

MCP server is available at `/mcp` endpoint of fastapps server. \
Example : https://your-public-url.trycloudflare.com/mcp

**Option A: Test on MCPJam Inspector**

Add your public URL + /mcp to ChatGPT.

```bash
npx @mcpjam/inspector@latest
```

**Option B: Test on ChatGPT**

Add your public URL + /mcp to ChatGPT's `"Settings > Connectors"` . 


## Creating More Widgets

```bash
uv run fastapps create additional-widget
```

### Using Widget Templates

FastApps provides pre-built templates to jumpstart your widget development:

```bash
# Create widget from a template
uv run fastapps create my-list --template list          # Vertical list with items
uv run fastapps create my-carousel --template carousel  # Horizontal scrolling cards
uv run fastapps create my-albums --template albums      # Photo gallery viewer
```


### Editing Your Widget

**You'll only need to edit these 2 folders:**

#### `server/tools/`

This folder contains backend `.py` files, where you define conditions & server logics for the app.

Example : 
```python 
### my_widget_tool.py
from fastapps import BaseWidget, Field, ConfigDict
from pydantic import BaseModel
from typing import Dict, Any

class MyWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(default="World")

class MyWidgetTool(BaseWidget):
    identifier = "my-widget"
    title = "My Widget"
    input_schema = MyWidgetInput
    invoking = "Processing..."
    invoked = "Done!"
    
    widget_csp = {
        "connect_domains": [],      # APIs you'll call
        "resource_domains": []      # Images/fonts you'll use
    }
    
    async def execute(self, input_data: MyWidgetInput) -> Dict[str, Any]:
        # Your logic here
        return {
            "name": input_data.name,
            "message": f"Hello, {input_data.name}!"
        }
```

#### `widgets/` - Frontend UI

The folder contains frontend component codes that will show up on the app screen according to the rules you've define with python codes above.

Apps in GPT components are react components - FastApps follows it. You can custom compoenents as you wish.

```jsx
// my-widget/index.jsx
import React from 'react';
import { useWidgetProps } from 'fastapps';

export default function MyWidget() {
  const props = useWidgetProps();
  
  return (
    <div style={{
      padding: '40px',
      textAlign: 'center',
      background: '#4A90E2',
      color: 'white',
      borderRadius: '12px'
    }}>
      <h1>{props.message}</h1>
      <p>Welcome, {props.name}!</p>
    </div>
  );
}
```

**That's it! These are the only files you need to write.**

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

- **[Contributing Guide](https://github.com/DooiLabs/FastApps/blob/main/CONTRIBUTING.md)** - How to contribute to FastApps
- **[Code Style Guide](https://github.com/DooiLabs/FastApps/blob/main/CODE_STYLE.md)** - Code formatting and style standards
- **[GitHub Workflows](https://github.com/DooiLabs/FastApps/blob/main/.github/WORKFLOWS.md)** - CI/CD documentation

### Quick Start for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/FastApps.git
cd FastApps

# Install uv (if not already installed)
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies (recommended - matches CI)
uv sync --dev

# Install pre-commit hooks (already installed via uv sync --dev)
uv run pre-commit install

# Make changes and ensure they pass checks
uv run black .
uv run ruff check --fix .
uv run pytest

# Submit a pull request
```

## License

MIT © Dooi Labs

## Links

- **PyPI**: https://pypi.org/project/fastapps/
- **React Hooks**: https://www.npmjs.com/package/fastapps
- **GitHub**: https://github.com/DooiLabs/FastApps
- **MCP Spec**: https://modelcontextprotocol.io/
