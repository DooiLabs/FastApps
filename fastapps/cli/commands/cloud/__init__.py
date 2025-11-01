"""FastApps Cloud CLI commands."""

import click

# Import subcommands
from .delete import delete
from .deploy import deploy
from .deployments import deployments
from .login import login
from .logout import logout
from .projects import projects
from .whoami import whoami


@click.group()
def cloud():
    """Manage FastApps Cloud deployments.

    Commands for authenticating, deploying, and managing your
    FastApps projects on FastApps Cloud.
    """
    pass


# Register subcommands
cloud.add_command(login)
cloud.add_command(logout)
cloud.add_command(whoami)
cloud.add_command(deploy)
cloud.add_command(deployments)
cloud.add_command(projects)  # projects includes link, unlink, status as subcommands
cloud.add_command(delete)


__all__ = ["cloud"]
