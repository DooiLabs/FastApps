"""Development server command with Cloudflare Tunnel integration."""

import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_cloudflared_installed() -> bool:
    """Check if cloudflared is installed."""
    try:
        subprocess.run(
            ["cloudflared", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_cloudflared() -> bool:
    """Install cloudflared automatically."""
    console.print("\n[cyan]Installing cloudflared...[/cyan]")

    system = platform.system()

    try:
        if system == "Darwin":  # macOS
            console.print("[dim]Using Homebrew...[/dim]")
            subprocess.run(
                ["brew", "install", "cloudflare/cloudflare/cloudflared"],
                check=True,
            )
        elif system == "Linux":
            console.print("[dim]Downloading binary...[/dim]")
            arch = platform.machine()
            if arch == "x86_64":
                arch = "amd64"
            elif arch == "aarch64":
                arch = "arm64"

            url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{arch}"

            subprocess.run(["wget", url, "-O", "/tmp/cloudflared"], check=True)
            subprocess.run(["chmod", "+x", "/tmp/cloudflared"], check=True)
            subprocess.run(["sudo", "mv", "/tmp/cloudflared", "/usr/local/bin/"], check=True)
        elif system == "Windows":
            console.print("[dim]Downloading Windows binary...[/dim]")
            subprocess.run([
                "powershell", "-Command",
                "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'C:\\Windows\\System32\\cloudflared.exe'"
            ], check=True)
        else:
            console.print(f"[red]Unsupported platform: {system}[/red]")
            return False

        console.print("[green]✓ cloudflared installed successfully[/green]\n")
        return True

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        console.print("\n[yellow]Manual installation:[/yellow]")
        console.print("  macOS:   brew install cloudflare/cloudflare/cloudflared")
        console.print("  Linux:   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
        console.print("  Windows: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
        return False


def start_cloudflare_tunnel(port: int) -> tuple[subprocess.Popen, str]:
    """
    Start Cloudflare Tunnel and return process and public URL.

    Returns:
        (process, public_url)
    """
    console.print(f"[cyan]Starting Cloudflare Tunnel on port {port}...[/cyan]")

    # Start cloudflared tunnel
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # Wait for tunnel URL
    public_url = None
    for _ in range(30):  # 30 seconds timeout
        if process.stderr:
            line = process.stderr.readline()
            if line:
                # Look for URL in output: https://random-name.trycloudflare.com
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    public_url = match.group(0)
                    break
        time.sleep(0.1)

    if not public_url:
        process.terminate()
        raise RuntimeError("Failed to get tunnel URL from cloudflared")

    return process, public_url


def start_dev_server(port=8001, host="0.0.0.0"):
    """Start development server with Cloudflare Tunnel."""

    # Check if we're in a FastApps project
    if not Path("server/main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        console.print(
            "[yellow]Run this command from your project root (where server/main.py exists)[/yellow]"
        )
        return False

    # Check if cloudflared is installed
    if not check_cloudflared_installed():
        console.print("[yellow]cloudflared not found[/yellow]")
        if not install_cloudflared():
            return False

    # Start Cloudflare Tunnel
    try:
        tunnel_process, public_url = start_cloudflare_tunnel(port)
    except RuntimeError as e:
        console.print(f"[red]Failed to start tunnel: {e}[/red]")
        return False

    console.print()

    # Import and start server (shows uvicorn boot logs first)
    console.print("[cyan]Starting FastApps server...[/cyan]\n")

    try:
        import uvicorn
        import asyncio

        # Import project server
        sys.path.insert(0, str(Path.cwd()))
        sys.argv.append("--build")  # Enable build mode for development
        from server.main import app

        # Create server config
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)

        # Start server in background thread to show info panel
        import threading
        import time

        def run_server():
            asyncio.run(server.serve())

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait a moment for server to start and show logs
        time.sleep(1)

        # Now display connection info (will stay visible above ongoing logs)
        console.print()
        table = Table(title="FastApps Development Server", title_style="bold green")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("URL", style="white")

        table.add_row("Local", f"http://{host}:{port}")
        table.add_row("Public", f"[bold green]{public_url}[/bold green]")

        console.print(table)
        console.print()

        # Display MCP endpoint info
        mcp_panel = Panel(
            f"[bold]MCP Server Endpoint:[/bold]\n"
            f"[green]{public_url}[/green]\n\n"
            f"[dim]Use this URL in your MCP client configuration[/dim]",
            title="Model Context Protocol",
            border_style="blue",
        )
        console.print(mcp_panel)
        console.print()

        console.print("[yellow]Press Ctrl+C to stop the server[/yellow]\n")

        # Keep main thread alive
        server_thread.join()

    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
        try:
            tunnel_process.terminate()
            tunnel_process.wait(timeout=5)
            console.print("[green]Server stopped[/green]")
        except Exception:
            pass
        return True

    except ImportError as e:
        console.print(f"[red]Error: Could not import server: {e}[/red]")
        console.print(
            "[yellow]Make sure you're in a FastApps project and dependencies are installed[/yellow]"
        )
        tunnel_process.terminate()
        return False

    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        tunnel_process.terminate()
        return False
