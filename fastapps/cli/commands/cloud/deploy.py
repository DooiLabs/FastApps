"""Deploy command for FastApps Cloud."""

import asyncio
import re
import secrets
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ....cloud.client import CloudClient
from ....cloud.config import CloudConfig
from ....cloud.projects_manager import ProjectsManager
from ....deployer import ArtifactPackager

console = Console()


def generate_random_suffix() -> str:
    """Generate a random 4-character suffix for project names."""
    return secrets.token_hex(2)


def validate_project_slug(slug: str) -> bool:
    """
    Validate project slug format.

    Rules:
    - Only lowercase letters, numbers, and hyphens
    - Must start with a letter or number
    - Must end with a letter or number
    - Length between 3 and 63 characters

    Args:
        slug: Project slug to validate

    Returns:
        True if valid, False otherwise
    """
    if not slug or len(slug) < 3 or len(slug) > 63:
        return False

    # Must match: lowercase letters, numbers, hyphens
    # Must start and end with letter or number
    pattern = r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$'
    return bool(re.match(pattern, slug))


def sanitize_to_slug(name: str) -> str:
    """
    Convert a name to a valid slug format.

    Args:
        name: Input name

    Returns:
        Sanitized slug
    """
    # Convert to lowercase
    slug = name.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)

    # Remove any characters that aren't alphanumeric or hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)

    return slug


async def handle_no_link() -> tuple[str, str, bool]:
    """
    Handle deployment when no project is linked.

    Returns:
        (project_id, project_name, should_link)
    """
    console.print("What would you like to do?")
    console.print("  [1] Create new project and link")
    console.print("  [2] Link to existing project")
    console.print()

    choice = console.input("Choose [1-2]: ")

    if choice == "1":
        # Create new project
        base_name = sanitize_to_slug(Path.cwd().name)
        suffix = generate_random_suffix()
        suggested_slug = f"{base_name}-{suffix}"

        console.print("\n[dim]Project slug requirements:[/dim]")
        console.print("[dim]  • Lowercase letters, numbers, and hyphens only[/dim]")
        console.print("[dim]  • 3-63 characters long[/dim]")
        console.print("[dim]  • Must start and end with letter or number[/dim]\n")

        # Loop until valid slug is provided
        while True:
            project_slug = console.input(f"Project slug [{suggested_slug}]: ") or suggested_slug

            if validate_project_slug(project_slug):
                break
            else:
                console.print("[red]✗ Invalid slug format[/red]")
                # Suggest sanitized version
                sanitized = sanitize_to_slug(project_slug)
                if sanitized and validate_project_slug(sanitized):
                    console.print(f"[yellow]Suggested: {sanitized}[/yellow]")
                console.print()

        console.print(f"\n[cyan]Creating project '{project_slug}'...[/cyan]")

        async with CloudClient() as client:
            project = await client.create_project(project_slug)

            project_id = project.get("id")

            if not project_id:
                console.print("[red]✗ Failed to create project[/red]")
                return None, None, False

            console.print(f"[green]✓ Project created: {project_id}[/green]")
            return project_id, project_slug, True  # Will link after deployment

    elif choice == "2":
        # Link to existing project
        console.print("\n[cyan]Fetching your projects...[/cyan]\n")

        async with CloudClient() as client:
            response = await client.list_projects()
            projects_list = response.get("projects", [])

            if not projects_list:
                console.print("[yellow]No projects found.[/yellow]")
                console.print("Please create a project first (option 1)")
                return None, None, False

            # Show projects
            from rich.table import Table as RichTable

            table = RichTable(show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim", width=4)
            table.add_column("Project ID", style="cyan")
            table.add_column("Deployments", justify="right")

            for idx, project in enumerate(projects_list, 1):
                table.add_row(
                    str(idx),
                    project.get("project_id", ""),
                    str(project.get("deployment_count", 0)),
                )

            console.print(table)
            console.print()

            # Select
            selection = console.input(f"Select project [1-{len(projects_list)}]: ")
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(projects_list):
                    selected = projects_list[idx]
                    project_id = selected.get("project_id")
                    project_name = selected.get("project_id")
                    return project_id, project_name, True
                else:
                    console.print("[red]Invalid selection[/red]")
                    return None, None, False
            except ValueError:
                console.print("[red]Invalid selection[/red]")
                return None, None, False

    else:
        console.print("[red]Invalid choice[/red]")
        return None, None, False


@click.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option("--no-build", is_flag=True, help="Skip widget build step")
@click.option("--project-id", help="Override project ID (default: from linked project)")
def deploy(yes, no_build, project_id):
    """Deploy your FastApps project to FastApps Cloud.

    This command will:
    1. Validate project structure
    2. Build widgets (unless --no-build)
    3. Authenticate (if not logged in)
    4. Package artifacts
    5. Upload and deploy to FastApps Cloud

    Examples:
        fastapps cloud deploy
        fastapps cloud deploy --yes
        fastapps cloud deploy --no-build --project-id my-project
    """
    asyncio.run(async_deploy(yes, no_build, project_id))


async def async_deploy(skip_confirmation: bool, skip_build: bool, project_id_override: str):
    """Async deployment workflow."""
    project_root = Path.cwd()

    # Step 1: Partial validation (without assets - will be built)
    console.print("\n[cyan]Validating project structure...[/cyan]")
    try:
        # Check required files/directories (except assets which is built)
        required_checks = {
            "package.json": project_root / "package.json",
            "requirements.txt": project_root / "requirements.txt",
            "server": project_root / "server",
            "server/main.py": project_root / "server" / "main.py",
            "widgets": project_root / "widgets",
        }

        for name, path in required_checks.items():
            if not path.exists():
                console.print(f"[red]✗ Required {'directory' if path.is_dir() or name in ['server', 'widgets'] else 'file'} '{name}' not found.[/red]")
                console.print("[dim]Make sure you're in a FastApps project root.[/dim]")
                return False

        console.print("[green]✓ Project structure valid[/green]")
    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        return False

    # Step 2: Check if build is needed and build widgets
    assets_dir = project_root / "assets"

    if not skip_build:
        # Check if assets exists
        if not assets_dir.exists():
            # Assets not found - ask user if they want to build
            console.print("\n[yellow]⚠️  Assets directory not found[/yellow]")
            if not skip_confirmation:
                console.print("[dim]Press Enter to confirm (default: yes)[/dim]")
                confirm = console.input("[bold]Build widgets now? (Y/n):[/bold] ").strip().lower()
                # Default to 'yes' on empty input
                if confirm and confirm not in ["y", "yes"]:
                    console.print("[yellow]Build cancelled. Cannot deploy without assets.[/yellow]")
                    return False

        # Build widgets (always rebuild to ensure latest state)
        console.print("\n[cyan]Building widgets...[/cyan]")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print("[green]✓ Widgets built successfully[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Build failed: {e.stderr}[/red]")
            console.print("[yellow]Tip: Run 'npm install' if packages are not installed[/yellow]")
            return False
        except FileNotFoundError:
            console.print("[red]✗ npm not found[/red]")
            return False
    else:
        # --no-build flag specified
        if not assets_dir.exists():
            console.print("\n[red]✗ Assets directory not found and --no-build specified[/red]")
            console.print("[yellow]Run 'npm run build' first or remove --no-build flag[/yellow]")
            return False
        console.print("\n[dim]Skipping build (--no-build specified)[/dim]")

    # Step 3: Check authentication first
    if not CloudConfig.is_logged_in():
        console.print("\n[yellow]You are not logged in.[/yellow]")
        console.print("[dim]Please run 'fastapps cloud login' first.[/dim]")
        return False

    # Step 4: Determine project ID
    project_id = None
    project_name = None
    should_link = False

    # Check if directory is linked to a project
    linked_project = ProjectsManager.get_linked_project(project_root)

    if project_id_override:
        # User explicitly specified project_id via flag
        project_id = project_id_override
        project_name = project_id_override
        console.print(f"\n[cyan]Using project:[/cyan] {project_id}")

    elif linked_project:
        # Use linked project
        project_id = linked_project["projectId"]
        project_name = linked_project["projectName"]
        console.print(f"\n[cyan]Deploying to:[/cyan] {project_name} ({project_id})")

    else:
        # No link → Interactive selection
        console.print("\n[yellow]⚠️  No project linked to this directory[/yellow]\n")

        project_id, project_name, should_link = await handle_no_link()
        if not project_id:
            return False

    # Count widgets
    assets_dir = project_root / "assets"
    console.print()

    # Step 5: Confirmation
    if not skip_confirmation:
        console.print("[dim]Press Enter to confirm (default: yes)[/dim]")
        confirm = console.input("[bold]Deploy to FastApps Cloud? (Y/n):[/bold] ").strip().lower()
        # Default to 'yes' on empty input
        if confirm and confirm not in ["y", "yes"]:
            console.print("[yellow]Deployment cancelled[/yellow]")
            return False

    # Step 6: Final validation before packaging
    try:
        packager = ArtifactPackager(project_root)
        packager._validate_project()
    except FileNotFoundError as e:
        console.print(f"\n[red]✗ Validation failed: {e}[/red]")
        console.print("[yellow]Make sure widgets are built and all required files exist.[/yellow]")
        return False

    # Step 7: Package artifacts
    console.print("\n[cyan]Packaging deployment artifacts...[/cyan]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Creating tarball...", total=None)
            tarball_path = packager.package()

        # Show tarball size
        tarball_size_mb = tarball_path.stat().st_size / (1024 * 1024)
        console.print(f"[green]✓ Package created ({tarball_size_mb:.2f} MB)[/green]")
    except Exception as e:
        console.print(f"[red]✗ Packaging failed: {e}[/red]")
        return False

    # Step 8: Upload and deploy
    console.print("\n[cyan]Deploying to FastApps Cloud...[/cyan]")

    try:
        async with CloudClient() as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                deploy_task = progress.add_task("Deploying safely...", total=None)

                # Status update callback
                def update_status(status: str, attempt: int, max_attempts: int):
                    status_messages = {
                        "pending": f"Queued... ({attempt}/{max_attempts})",
                        "building": f"Building application... ({attempt}/{max_attempts})",
                        "deploying": f"Deploying to production... ({attempt}/{max_attempts})",
                        "deployed": "Deployment complete!",
                        "failed": "Deployment failed",
                    }
                    message = status_messages.get(
                        status, f"Status: {status} ({attempt}/{max_attempts})"
                    )
                    progress.update(deploy_task, description=message)

                # Deploy - use project_name as the slug since server auto-creates projects
                deployment = await client.create_deployment(
                    tarball_path, project_name, status_callback=update_status
                )

        # Show success
        console.print("[green]✓ Deployment successful![/green]\n")

        # Update/create link if needed
        if should_link:
            ProjectsManager.link_project(project_id, project_name, project_root)
            console.print(f"[green]✓ Linked this directory to project[/green]\n")
        elif linked_project:
            # Update last deployment
            ProjectsManager.update_last_deployment(deployment.id, project_root)

        # Display deployment information
        if deployment.domain:
            success_panel = Panel(
                f"[bold green]Your app is live at:[/bold green]\n\n"
                f"[link=https://{deployment.domain}]https://{deployment.domain}[/link]\n\n"
                f"[dim]Deployment ID: {deployment.id}[/dim]\n"
                f"[dim]Project: {project_name} ({project_id})[/dim]\n\n",
                title="🚀 Deployment Complete",
                border_style="green",
            )
        else:
            success_panel = Panel(
                f"[bold green]Deployment Complete[/bold green]\n"
                f"[dim]Deployment ID: {deployment.id}[/dim]\n"
                f"[dim]Project: {project_name} ({project_id})[/dim]\n\n"
                f"[yellow]Domain information not available yet.[/yellow]\n"
                f"[dim]Check status: fastapps cloud deployments {deployment.id}[/dim]",
                title="🚀 Deployment Complete",
                border_style="green",
            )

        console.print(success_panel)
        return True

    except KeyboardInterrupt:
        console.print("\n\n[yellow]✗ Deployment cancelled by user[/yellow]")
        return False

    except RuntimeError as e:
        console.print(f"\n[red]✗ Deployment Failed[/red]\n")
        console.print(f"[yellow]{e}[/yellow]\n")

        if "Authentication expired" in str(e):
            console.print("[dim]Run 'fastapps cloud login' to re-authenticate.[/dim]")

        return False

    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error[/red]\n")
        console.print(f"[yellow]{type(e).__name__}: {e}[/yellow]\n")
        return False

    finally:
        # Always clean up tarball, regardless of success or failure
        tarball_path.unlink(missing_ok=True)
