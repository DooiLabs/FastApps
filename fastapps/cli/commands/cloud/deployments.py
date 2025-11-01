"""Deployments command for FastApps Cloud."""

import asyncio
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig

console = Console()


@click.command()
@click.argument("deployment_id", required=False)
@click.option("--limit", default=20, help="Maximum number of deployments to show")
def deployments(deployment_id, limit):
    """List or view deployment details.

    Without arguments: List all deployments
    With deployment_id: Show detailed information

    Examples:
        fastapps cloud deployments
        fastapps cloud deployments dep_abc123
        fastapps cloud deployments --limit 50
    """
    asyncio.run(async_deployments(deployment_id, limit))


async def async_deployments(deployment_id: str, limit: int):
    """Async deployments workflow."""
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Run 'fastapps cloud login' to authenticate.[/dim]")
        return

    try:
        async with CloudClient() as client:
            if deployment_id:
                # Show detailed deployment
                await show_deployment_detail(client, deployment_id)
            else:
                # List deployments
                await list_deployments(client, limit)

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


async def list_deployments(client: CloudClient, limit: int):
    """List all deployments."""
    deployments_list = await client.list_deployments(limit)

    if not deployments_list:
        console.print("\n[yellow]No deployments found.[/yellow]")
        console.print("[dim]Run 'fastapps cloud deploy' to create your first deployment.[/dim]\n")
        return

    # Create table
    table = Table(title="\nDeployments", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Project", style="white")
    table.add_column("Status", style="white")
    table.add_column("Domain", style="green")
    table.add_column("Created", style="dim")

    for dep in deployments_list:
        # Format status with color
        status_style = {
            "deployed": "[green]",
            "building": "[yellow]",
            "deploying": "[yellow]",
            "pending": "[dim]",
            "failed": "[red]",
        }.get(dep.status, "")
        status_text = f"{status_style}{dep.status}[/]"

        # Format domain
        domain_text = dep.domain if dep.domain else "[dim]-[/dim]"

        # Format date
        created_text = format_relative_time(dep.createdAt)

        table.add_row(
            dep.id[:12] + "...",
            dep.projectId or "[dim]unknown[/dim]",
            status_text,
            domain_text,
            created_text,
        )

    console.print(table)
    console.print()


async def show_deployment_detail(client: CloudClient, deployment_id: str):
    """Show detailed deployment information."""
    deployment = await client.get_deployment(deployment_id)

    # Create table for deployment details
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("ID", deployment.id)
    table.add_row("User ID", deployment.userId)
    if deployment.projectId:
        table.add_row("Project", deployment.projectId)

    # Status with color
    status_style = {
        "deployed": "[green]",
        "building": "[yellow]",
        "deploying": "[yellow]",
        "pending": "[dim]",
        "failed": "[red]",
    }.get(deployment.status, "")
    table.add_row("Status", f"{status_style}{deployment.status}[/]")

    if deployment.domain:
        table.add_row("Domain", f"[green]{deployment.domain}[/green]")
        table.add_row("URL", f"[link=https://{deployment.domain}]https://{deployment.domain}[/link]")

    if deployment.url:
        table.add_row("Provider URL", deployment.url)

    if deployment.deploymentId:
        table.add_row("Provider Deployment ID", deployment.deploymentId)

    if deployment.blobSize:
        size_mb = deployment.blobSize / (1024 * 1024)
        table.add_row("Size", f"{size_mb:.2f} MB")

    table.add_row("Created", deployment.createdAt)
    table.add_row("Updated", deployment.updatedAt)

    # Display in panel
    panel = Panel(
        table,
        title="[bold]Deployment Details[/bold]",
        border_style="cyan",
    )
    console.print()
    console.print(panel)
    console.print()


def format_relative_time(iso_timestamp: str) -> str:
    """Format ISO timestamp as relative time."""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"
    except Exception:
        return iso_timestamp
