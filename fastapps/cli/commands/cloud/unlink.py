"""Unlink command for FastApps Cloud."""

from pathlib import Path

import click
from rich.console import Console

from ....cloud.projects_manager import ProjectsManager

console = Console()


@click.command()
def unlink():
    """Unlink current directory from cloud project.

    Removes the link between this directory and its cloud project.
    This does NOT delete the project or deployments.

    Example:
        fastapps cloud projects unlink
    """
    cwd = Path.cwd()
    linked_project = ProjectsManager.get_linked_project(cwd)

    if not linked_project:
        console.print("\n[yellow]This directory is not linked to any project.[/yellow]\n")
        return

    project_name = linked_project["projectName"]
    project_id = linked_project["projectId"]

    # Unlink
    ProjectsManager.unlink_project(cwd)

    console.print(f"\n[green]✓ Unlinked[/green]")
    console.print(f"[dim]Directory:[/dim] {cwd}")
    console.print(f"[dim]Project:[/dim] {project_name} ({project_id})")
    console.print(f"\n[dim]The project and its deployments are still on the server.[/dim]")
    console.print(f"[dim]Run 'fastapps cloud link {project_id}' to relink.[/dim]\n")
