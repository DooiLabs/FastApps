"""Login command for FastApps Cloud."""

import asyncio

import click
from rich.console import Console

from ....cloud.config import CloudConfig
from ....deployer.auth import Authenticator

console = Console()


@click.command()
def login():
    """Login to FastApps Cloud.

    Opens your browser for OAuth authentication via Clerk.
    The access token will be saved to ~/.fastapps/config.json
    """
    asyncio.run(async_login())


async def async_login():
    """Async login workflow."""
    console.print("\n[cyan]FastApps Cloud Login[/cyan]\n")

    # Check if already logged in
    if CloudConfig.is_logged_in():
        # Verify token is still valid
        from ....cloud.client import CloudClient
        try:
            async with CloudClient() as client:
                await client.get_current_user()
            # Token is valid
            console.print("[yellow]You are already logged in.[/yellow]")
            confirm = console.input("Login again? (yes/no): ")
            if confirm.lower() not in ["yes", "y"]:
                console.print("[dim]Login cancelled.[/dim]")
                return
        except RuntimeError:
            # Token expired or invalid, proceed with login
            console.print("[yellow]Your session has expired.[/yellow]")
            console.print("[dim]Logging in again...[/dim]\n")

    cloud_url = CloudConfig.get_cloud_url()

    console.print(f"[dim]Server: {cloud_url}[/dim]")
    console.print("[dim]Your browser will open for authentication...[/dim]\n")

    try:
        # Callback to display auth URL after 1 second
        async def show_auth_url(url):
            await asyncio.sleep(1)
            console.print("[cyan]If browser didn't open, visit:[/cyan]")
            console.print(f"[link={url}]{url}[/link]\n")

        def url_callback(url):
            asyncio.create_task(show_auth_url(url))

        authenticator = Authenticator(cloud_url)
        token = await authenticator.authenticate(url_callback=url_callback)

        # Save token
        CloudConfig.set_token(token)

        console.print("[green]✓ Successfully logged in![/green]\n")

    except ConnectionError:
        console.print(f"\n[red]✗ Connection Error[/red]\n")
        console.print(f"[yellow]Cannot connect to FastApps Cloud:[/yellow]")
        console.print(f"[white]{cloud_url}[/white]\n")
        console.print("[dim]Please check your connection and server URL.[/dim]")
        return

    except TimeoutError:
        console.print(f"\n[red]✗ Authentication Timeout[/red]\n")
        console.print("[yellow]Authentication took too long (5 minutes limit)[/yellow]\n")
        console.print("[dim]Please try again.[/dim]")
        return

    except RuntimeError as e:
        error_msg = str(e)
        if "OAuth error" in error_msg:
            console.print(f"\n[red]✗ OAuth Error[/red]\n")
            console.print(f"[yellow]{error_msg}[/yellow]\n")
        elif "timed out" in error_msg.lower():
            console.print(f"\n[red]✗ Authentication Timeout[/red]\n")
            console.print("[yellow]Authentication took too long. Please try again.[/yellow]")
        else:
            console.print(f"\n[red]✗ Authentication Failed[/red]\n")
            console.print(f"[yellow]{error_msg}[/yellow]")
        return

    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error[/red]\n")
        console.print(f"[yellow]{type(e).__name__}: {e}[/yellow]\n")
        return
