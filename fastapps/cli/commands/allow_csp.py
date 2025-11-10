"""CSP management command for FastApps projects."""

import json
import sys
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def load_csp_config(project_root: Path) -> dict:
    """Load CSP configuration from fastapps.json."""
    config_file = project_root / "fastapps.json"

    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            console.print("[yellow]Warning: Could not parse fastapps.json[/yellow]")
            return {}

    return {}


def save_csp_config(project_root: Path, config: dict):
    """Save CSP configuration to fastapps.json."""
    config_file = project_root / "fastapps.json"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    console.print(f"[green]✓ Saved to {config_file}[/green]")


def add_csp_domain(
    url: str = None,
    domain_type: Literal["resource", "connect"] = None,
):
    """
    Add a domain to CSP allowlist.

    Args:
        url: Domain URL to allow (e.g., https://example.com)
        domain_type: Type of domain - "resource" for assets, "connect" for APIs
    """
    # Check if we're in a FastApps project
    project_root = Path.cwd()
    if not (project_root / "server" / "main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        console.print(
            "[yellow]Run this command from your project root (where server/main.py exists)[/yellow]"
        )
        return False

    # Interactive mode if arguments not provided
    if url is None:
        console.print("\n[cyan]Add CSP Domain[/cyan]\n")
        url = Prompt.ask(
            "[bold]Enter domain URL[/bold]",
            default="https://example.com"
        )

    if domain_type is None:
        console.print("\n[dim]Domain types:[/dim]")
        console.print("  [cyan]resource[/cyan] - For scripts, styles, images, fonts")
        console.print("  [cyan]connect[/cyan]  - For API calls (fetch, XHR)\n")

        domain_type = Prompt.ask(
            "[bold]Domain type[/bold]",
            choices=["resource", "connect"],
            default="resource"
        )

    # Validate URL
    if not url.startswith("https://") and not url.startswith("http://"):
        console.print("[red]Error: URL must start with https:// or http://[/red]")
        return False

    # Load existing config
    config = load_csp_config(project_root)

    # Initialize CSP section if not exists
    if "csp" not in config:
        config["csp"] = {
            "resource_domains": [],
            "connect_domains": []
        }

    # Add domain to appropriate list
    domain_key = f"{domain_type}_domains"
    if domain_key not in config["csp"]:
        config["csp"][domain_key] = []

    if url in config["csp"][domain_key]:
        console.print(f"[yellow]Domain already exists in {domain_type}_domains[/yellow]")
        return True

    config["csp"][domain_key].append(url)

    # Save config
    save_csp_config(project_root, config)

    # Show updated config
    console.print(f"\n[green]✓ Added {url} to {domain_type}_domains[/green]\n")
    show_csp_config(project_root)

    return True


def remove_csp_domain(
    url: str = None,
    domain_type: Literal["resource", "connect"] = None,
):
    """Remove a domain from CSP allowlist."""
    project_root = Path.cwd()
    if not (project_root / "server" / "main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        return False

    # Load existing config
    config = load_csp_config(project_root)

    if "csp" not in config:
        console.print("[yellow]No CSP configuration found[/yellow]")
        return False

    # Interactive mode if arguments not provided
    if url is None or domain_type is None:
        show_csp_config(project_root)
        console.print()

        if url is None:
            url = Prompt.ask("[bold]Enter domain URL to remove[/bold]")

        if domain_type is None:
            domain_type = Prompt.ask(
                "[bold]Domain type[/bold]",
                choices=["resource", "connect"]
            )

    # Remove domain
    domain_key = f"{domain_type}_domains"
    if domain_key in config["csp"] and url in config["csp"][domain_key]:
        config["csp"][domain_key].remove(url)
        save_csp_config(project_root, config)
        console.print(f"\n[green]✓ Removed {url} from {domain_type}_domains[/green]\n")
        show_csp_config(project_root)
        return True
    else:
        console.print(f"[yellow]Domain not found in {domain_type}_domains[/yellow]")
        return False


def show_csp_config(project_root: Path = None):
    """Display current CSP configuration."""
    if project_root is None:
        project_root = Path.cwd()

    config = load_csp_config(project_root)

    if "csp" not in config or (
        not config["csp"].get("resource_domains") and
        not config["csp"].get("connect_domains")
    ):
        console.print("[yellow]No CSP domains configured[/yellow]")
        return

    table = Table(title="CSP Configuration", title_style="bold cyan")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Domain", style="white")

    for domain in config["csp"].get("resource_domains", []):
        table.add_row("resource", domain)

    for domain in config["csp"].get("connect_domains", []):
        table.add_row("connect", domain)

    console.print(table)


def list_csp_domains():
    """List all configured CSP domains."""
    project_root = Path.cwd()
    if not (project_root / "server" / "main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        return False

    console.print()
    show_csp_config(project_root)
    console.print()

    return True
