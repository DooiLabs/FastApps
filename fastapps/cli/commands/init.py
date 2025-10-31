"""Initialize new FastApps project command."""

import contextlib
import io
import os
import subprocess
from pathlib import Path

from rich.console import Console

from fastapps.core.utils import get_cli_version

console = Console()

# Server main.py template
SERVER_MAIN_TEMPLATE = '''from pathlib import Path
import sys
import importlib
import inspect
import argparse
import re
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import FastApps framework
from fastapps import WidgetBuilder, WidgetMCPServer, BaseWidget, WidgetBuildResult
import uvicorn

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent / "tools"
ASSETS_DIR = PROJECT_ROOT / "assets"

def fetch_build_results() -> Dict[str, WidgetBuildResult]:
    """Parse built widget HTML files from assets directory."""
    results = {}
    for html_file in ASSETS_DIR.glob("*-*.html"):
        match = re.match(r"(.+)-([0-9a-f]{4})\\.html$", html_file.name)
        if match:
            name, hash_val = match.groups()
            results[name] = WidgetBuildResult(
                name=name, hash=hash_val, html=html_file.read_text()
            )
    return results

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
                        print(f"[OK] Loaded tool: {name} (identifier: {tool_identifier})")
                    else:
                        print(f"[WARNING] Warning: No build result found for tool '{tool_identifier}'")
        except Exception as e:
            print(f"[ERROR] Error loading {tool_file.name}: {e}")
    return tools

# Parse command-line arguments
parser = argparse.ArgumentParser(description="FastApps MCP Server")
parser.add_argument(
    "--build",
    action="store_true",
    help="Build widgets on startup (for development)"
)
args = parser.parse_args()

# Load build results
if args.build:
    # Build widgets on startup
    print(f"[INFO] Building widgets")
    builder = WidgetBuilder(PROJECT_ROOT)
    build_results = builder.build_all()
else:
    # Load pre-built widgets from assets directory
    print(f"[INFO] Loading pre-built widgets from assets")
    build_results = fetch_build_results()

# Auto-load and register tools
tools = auto_load_tools(build_results)

# Create MCP server
server = WidgetMCPServer(name="my-widgets", widgets=tools)

# Optional: Enable OAuth 2.1 authentication
# Uncomment and configure to protect your widgets with OAuth:
#
# server = WidgetMCPServer(
#     name="my-widgets",
#     widgets=tools,
#     auth_issuer_url="https://your-tenant.us.auth0.com",
#     auth_resource_server_url="https://yourdomain.com/mcp",
#     auth_required_scopes=["user"],
# )
#
# See docs: https://fastapps.dev/docs/auth

app = server.get_app()

if __name__ == "__main__":
    print(f"\\n[START] Starting server with {len(tools)} tools")
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''

REQUIREMENTS_TXT = f"""# All dependencies included in fastapps package
# pip install fastapps (or: uv pip install fastapps) is all you need!
fastapps>={get_cli_version()}
"""


def get_package_json(project_name: str) -> str:
    """Generate package.json content."""
    import json

    return json.dumps(
        {
            "name": project_name,
            "version": "1.0.0",
            "type": "module",
            "description": "Floydr ChatGPT widgets project",
            "scripts": {"build": "npx tsx node_modules/fastapps/build-all.mts"},
            "dependencies": {
                "fastapps": "^1.0.0",
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.3.4",
                "fast-glob": "^3.3.2",
                "tsx": "^4.19.2",
                "typescript": "^5.7.2",
                "vite": "^6.0.5",
            },
        },
        indent=2,
    )


PROJECT_README = """# {project_name}

ChatGPT widgets built with [FastApps](https://pypi.org/project/fastapps/).

## Quick Start

Your project includes an example widget (`my_widget`) to get you started!

```bash
fastapps dev
```

This will build your widgets and start the development server.

## Creating More Widgets

```bash
fastapps create another_widget
fastapps dev
```

## Project Structure

```
{project_name}/
├── server/
│   ├── main.py              # Server (auto-discovery)
│   └── tools/               # Widget backends
│       └── my_widget_tool.py   # Example widget
│
├── widgets/                 # Widget frontends
│   └── my_widget/
│       └── index.jsx        # Example React component
│
├── assets/                  # Built widgets (auto-generated)
└── package.json
```

## Learn More

- **FastApps Framework**: https://pypi.org/project/fastapps/
- **FastApps (React)**: https://www.npmjs.com/package/fastapps
- **Documentation**: https://github.com/fastapps-framework/fastapps

## License

MIT
"""

GITIGNORE = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
ENV/
env/
.venv

# JavaScript
node_modules/
npm-debug.log*
*.log
dist/
.cache/

# Build outputs
assets/
build-all.mts

# IDEs
.vscode/
.idea/
*.swp
.DS_Store
"""


def init_project(project_name: str):
    """Initialize a new Floydr project."""

    project_path = Path(project_name)

    # Check if directory exists
    if project_path.exists():
        console.print(f"[red][ERROR] Directory '{project_name}' already exists[/red]")
        return False

    console.print(
        f"[green]Creating FastApps project: [bold]{project_name}[/bold][/green]\n"
    )

    try:
        # Create directory structure
        console.print("Creating directory structure...")
        (project_path / "server" / "tools").mkdir(parents=True)
        (project_path / "server" / "api").mkdir(parents=True)
        (project_path / "widgets").mkdir(parents=True)

        # Create empty __init__.py files
        console.print("Creating Python modules...")
        (project_path / "server" / "__init__.py").write_text("")
        (project_path / "server" / "tools" / "__init__.py").write_text("")
        (project_path / "server" / "api" / "__init__.py").write_text("")

        # Create server/main.py
        console.print("Creating server...")
        (project_path / "server" / "main.py").write_text(SERVER_MAIN_TEMPLATE)

        # Create requirements.txt
        console.print("Creating requirements.txt...")
        (project_path / "requirements.txt").write_text(REQUIREMENTS_TXT)

        # Create package.json
        console.print("Creating package.json...")
        (project_path / "package.json").write_text(get_package_json(project_name))

        # Create README.md
        console.print("Creating README.md...")
        readme_content = PROJECT_README.format(project_name=project_name)
        (project_path / "README.md").write_text(readme_content)

        # Create .gitignore
        console.print("Creating .gitignore...")
        (project_path / ".gitignore").write_text(GITIGNORE)

        console.print(
            f"\n[green][OK] Project '{project_name}' created successfully![/green]"
        )

        # Create example widget
        console.print("\n[cyan]Creating example widget...[/cyan]")
        original_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            from .create import create_widget
            # Suppress the verbose output from create_widget
            with contextlib.redirect_stdout(io.StringIO()):
                create_widget("my_widget", auth_type=None, scopes=None)
            console.print("[green]Example widget created (my_widget)[/green]")
        finally:
            os.chdir(original_cwd)

        # Auto-install npm packages
        console.print("\n[cyan]Installing npm packages...[/cyan]")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            console.print("[green]npm packages installed[/green]")
        except FileNotFoundError:
            console.print("[yellow]npm not found. Run 'npm install' manually[/yellow]")
        except subprocess.CalledProcessError:
            console.print("[yellow]npm install failed. Run manually if needed[/yellow]")

        console.print("\n[green]All set![/green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"  [bold]cd {project_name}[/bold]")
        console.print("  [bold]fastapps dev[/bold]")
        console.print("\n[green]Happy building![/green]\n")

        return True

    except Exception as e:
        console.print(f"[red][ERROR] Error creating project: {e}[/red]")
        return False
