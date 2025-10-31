"""Delete command for FastApps Cloud."""

import asyncio

import click
from rich.console import Console

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig

console = Console()


@click.command()
@click.argument("deployment_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def delete(deployment_id, yes):
    """Delete a deployment.

    Permanently removes a deployment from FastApps Cloud.
    This action cannot be undone.

    Example:
        fastapps cloud delete dep_abc123
        fastapps cloud delete dep_abc123 --yes
    """
    asyncio.run(async_delete(deployment_id, yes))


async def async_delete(deployment_id: str, skip_confirmation: bool):
    """Async delete workflow."""
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Run 'fastapps cloud login' to authenticate.[/dim]")
        return

    try:
        async with CloudClient() as client:
            # Get deployment details first
            try:
                deployment = await client.get_deployment(deployment_id)
            except RuntimeError as e:
                if "not found" in str(e):
                    console.print(f"[red]✗ Deployment {deployment_id} not found[/red]")
                    return
                raise

            # Show warning
            console.print(f"\n[bold red]⚠️  Warning[/bold red]")
            console.print(f"This will permanently delete deployment: [cyan]{deployment.id}[/cyan]")
            if deployment.projectId:
                console.print(f"Project: [white]{deployment.projectId}[/white]")
            if deployment.domain:
                console.print(f"Domain: [green]{deployment.domain}[/green]")
            console.print()

            # Confirmation
            if not skip_confirmation:
                confirm = console.input("[bold]Continue? (yes/no):[/bold] ")
                if confirm.lower() not in ["yes", "y"]:
                    console.print("[dim]Deletion cancelled.[/dim]")
                    return

            # Delete
            await client.delete_deployment(deployment_id)
            console.print(f"[green]✓ Deployment {deployment_id} deleted successfully[/green]\n")

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
