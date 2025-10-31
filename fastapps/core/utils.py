from importlib.metadata import version

__version__ = version("fastapps")

def get_cli_version() -> str:
    """Get the current version of FastApps."""
    return __version__