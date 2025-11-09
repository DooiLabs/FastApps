"""CLI utility functions."""

from rich.console import Console

console = Console()


def print_uv_installation_message():
    """Print uv installation instructions."""
    console.print("\n[red][ERROR] uv is not installed[/red]")
    console.print("\n[yellow]Please install uv first:[/yellow]")
    console.print("  [dim]curl -LsSf https://astral.sh/uv/install.sh | sh[/dim]")
    console.print(
        "\n[dim]For more information, visit: https://github.com/astral-sh/uv[/dim]"
    )
    console.print()


def print_uv_command_suggestion(command: str, description: str = ""):
    """Print a uv command suggestion with context.

    Args:
        command: The uv command to suggest
        description: Optional description of what the command does
    """
    console.print(f"\n[cyan]Suggested command:[/cyan]")
    console.print(f"  [green]{command}[/green]")
    if description:
        console.print(f"  [dim]{description}[/dim]")
    console.print()


def print_missing_dependencies(missing_deps: list[str]):
    """Print missing dependencies with installation suggestion.

    Args:
        missing_deps: List of missing dependency names
    """
    if not missing_deps:
        return

    console.print("\n[yellow]⚠ Missing dependencies:[/yellow]")
    for dep in missing_deps:
        console.print(f"  - {dep}")

    install_command = f"uv add {' '.join(missing_deps)}"
    print_uv_command_suggestion(install_command, "Add missing dependencies")
