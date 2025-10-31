"""FastApps CLI - Command-line interface for the FastApps framework."""

import click
from rich.console import Console

from .commands.build import build_command
from .commands.cloud import cloud
from .commands.create import create_widget
from .commands.dev import start_dev_server
from .commands.init import init_project
from .commands.use import use_integration

console = Console()

# Get version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("fastapps")
except Exception:
    __version__ = "unknown"


@click.group()
@click.version_option(version=__version__, prog_name="fastapps")
def cli():
    """FastApps - ChatGPT Widget Framework

    Build interactive ChatGPT widgets with zero boilerplate.
    Supports OAuth 2.1 authentication for secure widgets.
    """
    pass


@cli.command()
@click.argument("project_name")
def init(project_name):
    """Initialize a new FastApps project.

    Example:
        fastapps init myproject

    Creates a complete project structure with:
    - server/main.py (auto-discovery)
    - server/tools/ (for widget backends)
    - widgets/ (for React components)
    - requirements.txt
    - package.json
    """
    init_project(project_name)


@cli.command()
@click.argument("widget_name")
@click.option("--auth", is_flag=True, help="Add auth_required decorator to widget")
@click.option("--public", is_flag=True, help="Add no_auth decorator (public widget)")
@click.option("--optional-auth", is_flag=True, help="Add optional_auth decorator")
@click.option("--scopes", help="OAuth scopes (comma-separated, e.g., 'user,read:data')")
def create(widget_name, auth, public, optional_auth, scopes):
    """Create a new widget with tool and component files.

    Examples:
        fastapps create mywidget
        fastapps create mywidget --auth --scopes user,read:data
        fastapps create mywidget --public
        fastapps create mywidget --optional-auth --scopes user

    Authentication options:
        --auth: Require OAuth authentication
        --public: Mark as public (no auth)
        --optional-auth: Support both authenticated and anonymous
        --scopes: OAuth scopes to require
    """
    # Parse scopes
    scope_list = scopes.split(",") if scopes else None

    # Validate options
    option_count = sum([auth, public, optional_auth])
    if option_count > 1:
        console.print(
            "[red]Error: Only one auth option allowed (--auth, --public, or --optional-auth)[/red]"
        )
        return

    # Determine auth type
    auth_type = None
    if auth:
        auth_type = "required"
    elif public:
        auth_type = "none"
    elif optional_auth:
        auth_type = "optional"

    create_widget(widget_name, auth_type=auth_type, scopes=scope_list)


@cli.command()
@click.option("--port", default=8001, help="Port to run the server on (default: 8001)")
@click.option(
    "--host", default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)"
)
def dev(port, host):
    """Start development server with Cloudflare Tunnel.

    This command will:
    1. Build widgets
    2. Install cloudflared if needed (automatic, no token required)
    3. Start a public Cloudflare Tunnel
    4. Launch the FastApps development server
    5. Display public and local URLs

    Example:
        fastapps dev
        fastapps dev --port 8080

    Note: Uses Cloudflare Tunnel (free, unlimited, no sign-up required)
    """
    start_dev_server(port=port, host=host)


@cli.command()
def build():
    """Build widgets for production."""
    build_command()


# Register cloud command group
cli.add_command(cloud)


@cli.command()
def auth_info():
    """Show authentication setup information."""
    console.print("\n[bold cyan]FastApps Authentication Guide[/bold cyan]")
    console.print("\n[yellow]Server-Wide Auth:[/yellow]")
    console.print("  Configure in server/main.py:")
    console.print("  [dim]server = WidgetMCPServer([/dim]")
    console.print("  [dim]    name='my-widgets',[/dim]")
    console.print("  [dim]    widgets=tools,[/dim]")
    console.print("  [dim]    auth_issuer_url='https://tenant.auth0.com',[/dim]")
    console.print(
        "  [dim]    auth_resource_server_url='https://example.com/mcp',[/dim]"
    )
    console.print("  [dim]    auth_required_scopes=['user'],[/dim]")
    console.print("  [dim])[/dim]")

    console.print("\n[yellow]Per-Widget Auth:[/yellow]")
    console.print("  Create authenticated widget:")
    console.print(
        "  [dim]$ fastapps create mywidget --auth --scopes user,read:data[/dim]"
    )
    console.print("\n  Create public widget:")
    console.print("  [dim]$ fastapps create mywidget --public[/dim]")
    console.print("\n  Create optional auth widget:")
    console.print(
        "  [dim]$ fastapps create mywidget --optional-auth --scopes user[/dim]"
    )

    console.print("\n[yellow]Decorators:[/yellow]")
    console.print(
        "  [green]@auth_required[/green](scopes=['user']) - Require authentication"
    )
    console.print("  [green]@no_auth[/green] - Public widget (opt-out)")
    console.print("  [green]@optional_auth[/green](scopes=['user']) - Works both ways")

    console.print("\n[yellow]UserContext:[/yellow]")
    console.print("  Access authenticated user in execute():")
    console.print("  [dim]async def execute(self, input_data, context, user):[/dim]")
    console.print("  [dim]    if user.is_authenticated:[/dim]")
    console.print("  [dim]        return {'user_id': user.subject}[/dim]")

    console.print("\n[cyan]Documentation:[/cyan]")
    console.print("  Server auth: docs/08-AUTH.md")
    console.print("  Per-widget auth: docs/09-PER-WIDGET-AUTH.md")
    console.print()


@cli.command()
@click.argument("integration_name")
def use(integration_name):
    """Add integrations to your FastApps project.

    Available integrations:
        metorial - Add Metorial MCP integration for querying data sources

    Example:
        fastapps use metorial

    This will create server/api/metorial_mcp.py with environment variable support.
    """
    use_integration(integration_name)


if __name__ == "__main__":
    cli()
