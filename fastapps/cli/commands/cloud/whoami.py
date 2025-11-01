"""Whoami command for FastApps Cloud."""

import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig

console = Console()


@click.command()
def whoami():
    """Show current logged-in user information.

    Displays your FastApps Cloud user details including
    ID, email, username, and GitHub username.
    """
    asyncio.run(async_whoami())


async def async_whoami():
    """Async whoami workflow."""
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Run 'fastapps cloud login' to authenticate.[/dim]")
        return

    try:
        async with CloudClient() as client:
            user = await client.get_current_user()

            # Create table for user info
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            if user.email:
                table.add_row("Email", user.email)
            if user.username:
                table.add_row("Username", f"@{user.username}")
            if user.github_username:
                table.add_row("GitHub", user.github_username)

            # Display in panel
            panel = Panel(
                table,
                title="[bold]User Information[/bold]",
                border_style="green",
            )
            console.print()
            console.print(panel)
            console.print()

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
