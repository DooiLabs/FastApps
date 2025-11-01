"""Logout command for FastApps Cloud."""

import click
from rich.console import Console

from ....cloud.config import CloudConfig

console = Console()


@click.command()
def logout():
    """Logout from FastApps Cloud.

    Removes the saved authentication token from ~/.fastapps/config.json
    """
    if not CloudConfig.is_logged_in():
        console.print("[yellow]You are not logged in.[/yellow]")
        return

    CloudConfig.clear_token()
    console.print("[green]✓ Logged out successfully[/green]")
