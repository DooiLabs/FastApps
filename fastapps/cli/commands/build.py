"""Build command for FastApps."""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def build_command():
    """Build widgets for production.

    Compiles all widgets in the widgets/ directory to optimized HTML/JS bundles.
    """
    project_root = Path.cwd()

    # Check if package.json exists and has a build script
    package_json = project_root / "package.json"
    if not package_json.exists():
        console.print("[red]✗ package.json not found[/red]")
        console.print("[dim]Make sure you're in a FastApps project root[/dim]")
        return False

    try:
        console.print("[cyan]Building widgets...[/cyan]")

        # Use npm run build if available
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print("[green]✓ Build completed successfully[/green]")
            if result.stdout:
                console.print(result.stdout)
            return True
        else:
            console.print("[red]✗ Build failed[/red]")
            if result.stderr:
                console.print(f"[yellow]{result.stderr}[/yellow]")
            return False

    except ImportError:
        console.print("[red]✗ FastApps package not found[/red]")
        console.print("[dim]Make sure fastapps is installed[/dim]")
        return False
    except FileNotFoundError:
        console.print("[red]✗ npx or tsx not found[/red]")
        console.print("[dim]Make sure Node.js and tsx are installed[/dim]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Build error: {e}[/red]")
        return False
