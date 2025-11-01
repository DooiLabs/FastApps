"""Link command for FastApps Cloud."""

import asyncio
import secrets
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig
from ....cloud.projects_manager import ProjectsManager

console = Console()


def generate_random_suffix() -> str:
    """Generate a random 4-character suffix for project names."""
    return secrets.token_hex(2)


@click.command()
@click.argument("project_id", required=False)
def link(project_id):
    """Link current directory to a cloud project.

    Without project_id: Shows interactive project selector
    With project_id: Links directly to specified project

    Examples:
        fastapps cloud projects link
        fastapps cloud projects link proj_abc123
    """
    asyncio.run(async_link(project_id))


async def async_link(project_id: str):
    """Async link workflow."""
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Run 'fastapps cloud login' to authenticate.[/dim]")
        return

    cwd = Path.cwd()

    # Check if already linked
    existing = ProjectsManager.get_linked_project(cwd)
    if existing:
        console.print(
            f"\n[yellow]⚠️  This directory is already linked to:[/yellow]"
        )
        console.print(f"   {existing['projectName']} ({existing['projectId']})\n")

        confirm = Prompt.ask("Relink to a different project?", choices=["yes", "no"], default="no")
        if confirm != "yes":
            console.print("[dim]Link cancelled.[/dim]")
            return

    try:
        async with CloudClient() as client:
            if project_id:
                # Direct link with project_id
                await link_to_project(client, project_id, cwd)
            else:
                # Interactive selector
                await interactive_link(client, cwd)

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


async def link_to_project(client: CloudClient, project_id: str, cwd: Path):
    """Link to a specific project by ID."""
    # Fetch project details to verify it exists
    try:
        project_data = await client.get_project(project_id)
        project_name = project_data.get("project_id", project_id)  # Use ID as fallback

        # Link
        ProjectsManager.link_project(project_id, project_name, cwd)

        console.print(f"\n[green]✓ Linked[/green]")
        console.print(f"[dim]Directory:[/dim] {cwd}")
        console.print(f"[dim]Project:[/dim] {project_name} ({project_id})\n")

    except RuntimeError as e:
        if "not found" in str(e):
            console.print(f"\n[red]✗ Project {project_id} not found[/red]\n")
        else:
            raise


async def interactive_link(client: CloudClient, cwd: Path):
    """Interactive project selection."""
    console.print("\n[cyan]Select a project to link:[/cyan]\n")

    # Fetch projects
    response = await client.list_projects()
    projects_list = response.get("projects", [])

    if not projects_list:
        console.print("[yellow]No projects found.[/yellow]")
        console.print("\n[cyan]Would you like to create a new project?[/cyan]")

        create = Prompt.ask("Create new project?", choices=["yes", "no"], default="yes")
        if create == "yes":
            await create_and_link_project(client, cwd)
        return

    # Show projects table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Project ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Deployments", justify="right")

    for idx, project in enumerate(projects_list, 1):
        table.add_row(
            str(idx),
            project.get("project_id", ""),
            project.get("project_id", ""),  # Using ID as name for now
            str(project.get("deployment_count", 0)),
        )

    console.print(table)
    console.print()

    # Add "Create new" option
    console.print(f"[cyan][{len(projects_list) + 1}][/cyan] Create new project")
    console.print()

    # Get selection
    max_choice = len(projects_list) + 1
    choice = Prompt.ask(
        "Select project",
        default="1",
    )

    try:
        choice_num = int(choice)
        if choice_num < 1 or choice_num > max_choice:
            console.print("[red]Invalid selection[/red]")
            return
    except ValueError:
        console.print("[red]Invalid selection[/red]")
        return

    if choice_num == max_choice:
        # Create new project
        await create_and_link_project(client, cwd)
    else:
        # Link to selected project
        selected_project = projects_list[choice_num - 1]
        project_id = selected_project.get("project_id")
        project_name = selected_project.get("project_id")  # Using ID as name

        ProjectsManager.link_project(project_id, project_name, cwd)

        console.print(f"\n[green]✓ Linked[/green]")
        console.print(f"[dim]Directory:[/dim] {cwd}")
        console.print(f"[dim]Project:[/dim] {project_name} ({project_id})\n")


async def create_and_link_project(client: CloudClient, cwd: Path):
    """Create a new project and link to it."""
    # Get project name with random suffix
    base_name = cwd.name
    suffix = generate_random_suffix()
    suggested_name = f"{base_name}-{suffix}"
    project_name = Prompt.ask("Project name", default=suggested_name)

    console.print(f"\n[cyan]Creating project '{project_name}'...[/cyan]")

    # Create project on server
    project = await client.create_project(project_name)
    project_id = project.get("id")

    if not project_id:
        console.print("[red]✗ Failed to create project[/red]")
        return

    # Link
    ProjectsManager.link_project(project_id, project_name, cwd)

    console.print(f"\n[green]✓ Project created and linked[/green]")
    console.print(f"[dim]Directory:[/dim] {cwd}")
    console.print(f"[dim]Project:[/dim] {project_name} ({project_id})\n")
