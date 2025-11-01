"""Status command for FastApps Cloud."""

import asyncio
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig
from ....cloud.projects_manager import ProjectsManager

console = Console()


@click.command()
def status():
    """Show current project status.

    Displays information about the project linked to current directory,
    including last deployment status.

    Example:
        fastapps cloud projects status
    """
    asyncio.run(async_status())


async def async_status():
    """Async status workflow."""
    cwd = Path.cwd()
    linked_project = ProjectsManager.get_linked_project(cwd)

    if not linked_project:
        console.print("\n[yellow]⚠️  No project linked to this directory[/yellow]")
        console.print("[dim]Run 'fastapps cloud link' to connect to a project[/dim]\n")
        return

    # Build status table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Directory", str(cwd))
    table.add_row("Project ID", linked_project["projectId"])
    table.add_row("Project Name", linked_project["projectName"])

    # Format linked time
    linked_at = linked_project.get("linkedAt")
    if linked_at:
        try:
            dt = datetime.fromisoformat(linked_at.replace("Z", "+00:00"))
            now = datetime.now(dt.tzinfo)
            diff = now - dt
            if diff.days > 0:
                linked_ago = f"{diff.days}d ago"
            elif diff.seconds > 3600:
                linked_ago = f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60:
                linked_ago = f"{diff.seconds // 60}m ago"
            else:
                linked_ago = "just now"
            table.add_row("Linked", linked_ago)
        except Exception:
            pass

    # Fetch last deployment if authenticated
    last_dep_id = linked_project.get("lastDeployment")
    if last_dep_id and CloudConfig.is_logged_in():
        try:
            async with CloudClient() as client:
                deployment = await client.get_deployment(last_dep_id)
                status_style = {
                    "deployed": "[green]",
                    "building": "[yellow]",
                    "deploying": "[yellow]",
                    "pending": "[dim]",
                    "failed": "[red]",
                }.get(deployment.status, "")
                table.add_row(
                    "Last Deployment",
                    f"{status_style}{deployment.status}[/] ({last_dep_id[:12]}...)"
                )
                if deployment.domain:
                    table.add_row("Domain", f"[green]{deployment.domain}[/green]")
        except Exception:
            # Ignore errors fetching deployment
            pass

    # Display panel
    panel = Panel(
        table,
        title="[bold]Project Status[/bold]",
        border_style="cyan",
    )
    console.print()
    console.print(panel)
    console.print()
