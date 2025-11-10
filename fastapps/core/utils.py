import subprocess
from functools import wraps
from importlib.metadata import version

__version__ = version("fastapps")


def get_cli_version() -> str:
    """Get current version of FastApps."""
    return __version__


def is_uv_installed() -> bool:
    """Check if uv is installed and available."""
    try:
        run_uv_command(["--version"])
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def run_uv_command(args, cwd=None):
    """Run uv command with proper error handling.

    Args:
        args: List of command arguments
        cwd: Working directory for command

    Returns:
        subprocess.CompletedProcess result

    Raises:
        FileNotFoundError: If uv is not installed
        subprocess.CalledProcessError: If uv command fails
    """
    try:
        return subprocess.run(
            ["uv"] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "uv is not installed. Please install uv first:\n"
            "curl -LsSf https://astral.sh/uv/install.sh | sh"
        )


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed using uv pip show.

    Args:
        package_name: Name of the package to check

    Returns:
        True if package is installed, False otherwise
    """
    try:
        run_uv_command(["pip", "show", package_name])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def handle_uv_command_error(func):
    """Decorator to handle uv command errors consistently."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "\n[red][ERROR] uv is not installed. Please install uv first:[/red]\n"
            )
            print("[yellow]curl -LsSf https://astral.sh/uv/install.sh | sh[/yellow]\n")
            print(
                "[yellow]Or visit: https://github.com/astral-sh/uv#installation[/yellow]\n"
            )
            raise
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                e.returncode, e.cmd, f"uv command failed: {e.stderr}"
            )

    return wrapper


def safe_check_dependencies(deps: list[str]) -> list[str]:
    """Safely check multiple dependencies with consistent error handling.

    Args:
        deps: List of package names to check

    Returns:
        List of missing dependencies
    """
    missing = []
    for dep in deps:
        try:
            if not is_package_installed(dep):
                missing.append(dep)
        except (FileNotFoundError, subprocess.CalledProcessError):
            # If uv is not available, assume all are missing
            missing = deps.copy()
            break
    return missing


def check_uv_installation() -> bool:
    """Check if uv is installed and provide installation instructions if not.

    Returns:
        True if uv is installed, False otherwise
    """
    if is_uv_installed():
        return True

    return False
