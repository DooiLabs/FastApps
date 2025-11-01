"""Projects command for FastApps Cloud."""

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


@click.group()
def projects():
    """Manage projects and project links.

    Commands:
        list    - List cloud projects or show project details
        link    - Link current directory to a project
        unlink  - Unlink current directory from a project
        status  - Show current directory's project status

    Examples:
        fastapps cloud projects list
        fastapps cloud projects list --linked
        fastapps cloud projects list my-project
        fastapps cloud projects link
        fastapps cloud projects status
    """
    pass


@click.command()
@click.argument("project_id", required=False)
@click.option("--linked", is_flag=True, help="Show locally linked projects")
def list(project_id, linked):
    """List cloud projects or show project details.

    Without arguments: List all projects from cloud
    With --linked: Show all locally linked directories
    With project_id: Show detailed project information with all deployments

    Examples:
        fastapps cloud projects list
        fastapps cloud projects list --linked
        fastapps cloud projects list my-project
    """
    asyncio.run(async_projects(project_id, linked))


async def async_projects(project_id: str, show_linked: bool):
    """Async projects workflow."""
    # Handle --linked flag (doesn't require authentication)
    if show_linked:
        show_linked_projects()
        return

    # Cloud operations require authentication
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Run 'fastapps cloud login' to authenticate.[/dim]")
        return

    try:
        async with CloudClient() as client:
            if project_id:
                # Show detailed project
                await show_project_detail(client, project_id)
            else:
                # List projects
                await list_projects(client)

    except RuntimeError as e:
        error_msg = str(e)
        console.print(f"\n[red]✗ Error[/red]")
        console.print(f"[yellow]{error_msg}[/yellow]\n")

        if "Authentication expired" in error_msg:
            console.print("[dim]Run 'fastapps cloud login' to re-authenticate.[/dim]")
        elif "Network error" in error_msg:
            console.print("[dim]Please check your connection and server status:[/dim]")
            console.print(f"[dim]Server: {CloudConfig.get_cloud_url()}[/dim]")
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error[/red]")
        console.print(f"[yellow]{type(e).__name__}: {e}[/yellow]\n")


def show_linked_projects():
    """Show all locally linked projects."""
    projects = ProjectsManager.load_projects()

    if not projects:
        console.print("\n[yellow]No linked projects found.[/yellow]")
        console.print("[dim]Run 'fastapps cloud link' to link a project to a directory.[/dim]\n")
        return

    # Create table
    table = Table(title="\nLinked Projects", show_lines=False)
    table.add_column("Directory", style="cyan", no_wrap=False)
    table.add_column("Project ID", style="white")
    table.add_column("Project Name", style="white")
    table.add_column("Linked", style="dim")
    table.add_column("Last Deployment", style="green", no_wrap=True)

    for cwd_str, project_info in projects.items():
        directory = Path(cwd_str).name  # Show just the directory name
        project_id = project_info.get("projectId", "-")
        project_name = project_info.get("projectName", "-")
        linked_at = project_info.get("linkedAt", "")
        last_deployment = project_info.get("lastDeployment")

        # Format linked time
        linked_ago = ""
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
            except Exception:
                linked_ago = "-"

        # Format last deployment
        last_dep_text = last_deployment[:12] + "..." if last_deployment else "[dim]-[/dim]"

        table.add_row(
            f"[dim]{cwd_str}[/dim]",
            project_id,
            project_name,
            linked_ago,
            last_dep_text,
        )

    console.print(table)
    console.print()


async def list_projects(client: CloudClient):
    """List all projects."""
    response = await client.list_projects()
    projects_list = response.get("projects", [])

    if not projects_list or len(projects_list) == 0:
        console.print("\n[yellow]No projects found.[/yellow]")
        console.print("[dim]Run 'fastapps cloud deploy' to create your first project.[/dim]\n")
        return

    # Create table
    table = Table(title="\nProjects", show_lines=False)
    table.add_column("Project ID", style="cyan", no_wrap=True)
    table.add_column("Deployments", style="white", justify="right")
    table.add_column("Latest Status", style="white")
    table.add_column("Latest Domain", style="green")

    for project_info in projects_list:
        project_id = project_info.get("project_id", "unknown")
        deployment_count = project_info.get("deployment_count", 0)
        latest_status = project_info.get("latest_status")
        latest_domain = project_info.get("latest_domain")

        # Format status with color
        if latest_status:
            status_style = {
                "deployed": "[green]",
                "building": "[yellow]",
                "deploying": "[yellow]",
                "pending": "[dim]",
                "failed": "[red]",
            }.get(latest_status, "")
            status_text = f"{status_style}{latest_status}[/]"
        else:
            status_text = "[dim]-[/dim]"

        # Format domain
        domain_text = latest_domain if latest_domain else "[dim]-[/dim]"

        table.add_row(
            project_id,
            str(deployment_count),
            status_text,
            domain_text,
        )

    console.print(table)
    console.print()


async def show_project_detail(client: CloudClient, project_id: str):
    """Show detailed project information."""
    project_data = await client.get_project(project_id)

    deployments = project_data.get("deployments", [])

    # Create summary panel
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column("Field", style="cyan")
    summary.add_column("Value", style="white")

    summary.add_row("Project ID", project_id)
    summary.add_row("Total Deployments", str(len(deployments)))

    if deployments:
        latest = deployments[0]
        latest_status = latest.get("status", "unknown")
        status_style = {
            "deployed": "[green]",
            "building": "[yellow]",
            "deploying": "[yellow]",
            "pending": "[dim]",
            "failed": "[red]",
        }.get(latest_status, "")
        summary.add_row("Latest Status", f"{status_style}{latest_status}[/]")

        if latest.get("domain"):
            summary.add_row("Latest Domain", f"[green]{latest['domain']}[/green]")

    panel = Panel(
        summary,
        title="[bold]Project Details[/bold]",
        border_style="cyan",
    )
    console.print()
    console.print(panel)

    # Show deployments table
    if deployments:
        console.print("\n[bold]Deployments:[/bold]\n")

        table = Table(show_lines=False)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Domain", style="green")
        table.add_column("Created", style="dim")

        for dep in deployments:
            status = dep.get("status", "unknown")
            status_style = {
                "deployed": "[green]",
                "building": "[yellow]",
                "deploying": "[yellow]",
                "pending": "[dim]",
                "failed": "[red]",
            }.get(status, "")
            status_text = f"{status_style}{status}[/]"

            domain_text = dep.get("domain") or "[dim]-[/dim]"

            table.add_row(
                dep.get("id", "")[:12] + "...",
                status_text,
                domain_text,
                dep.get("createdAt", ""),
            )

        console.print(table)

    console.print()


# Import and register subcommands
from .link import link as link_cmd
from .status import status as status_cmd
from .unlink import unlink as unlink_cmd

projects.add_command(list)
projects.add_command(link_cmd, name="link")
projects.add_command(unlink_cmd, name="unlink")
projects.add_command(status_cmd, name="status")
