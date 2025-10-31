"""Manages local directory to cloud project mappings."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import CloudConfig


class ProjectsManager:
    """Manages mappings between local directories and cloud projects."""

    @staticmethod
    def get_projects_file() -> Path:
        """Get projects mapping file path."""
        return CloudConfig.get_config_dir() / "projects.json"

    @staticmethod
    def load_projects() -> dict:
        """Load projects mapping from file."""
        projects_file = ProjectsManager.get_projects_file()
        if projects_file.exists():
            try:
                with open(projects_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_projects(projects: dict):
        """Save projects mapping to file."""
        projects_file = ProjectsManager.get_projects_file()
        try:
            with open(projects_file, "w") as f:
                json.dump(projects, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def get_linked_project(cwd: Optional[Path] = None) -> Optional[dict]:
        """
        Get project linked to current directory.

        Args:
            cwd: Directory path (defaults to current directory)

        Returns:
            Project info dict or None if not linked
        """
        if cwd is None:
            cwd = Path.cwd()

        cwd_str = str(cwd.resolve())
        projects = ProjectsManager.load_projects()
        return projects.get(cwd_str)

    @staticmethod
    def link_project(
        project_id: str, project_name: str, cwd: Optional[Path] = None
    ):
        """
        Link current directory to a project.

        Args:
            project_id: Cloud project ID
            project_name: Project name
            cwd: Directory path (defaults to current directory)
        """
        if cwd is None:
            cwd = Path.cwd()

        cwd_str = str(cwd.resolve())
        projects = ProjectsManager.load_projects()

        projects[cwd_str] = {
            "projectId": project_id,
            "projectName": project_name,
            "linkedAt": datetime.utcnow().isoformat() + "Z",
            "lastDeployment": None,
        }

        ProjectsManager.save_projects(projects)

    @staticmethod
    def update_last_deployment(deployment_id: str, cwd: Optional[Path] = None):
        """
        Update last deployment ID for linked project.

        Args:
            deployment_id: Deployment ID
            cwd: Directory path (defaults to current directory)
        """
        if cwd is None:
            cwd = Path.cwd()

        cwd_str = str(cwd.resolve())
        projects = ProjectsManager.load_projects()

        if cwd_str in projects:
            projects[cwd_str]["lastDeployment"] = deployment_id
            ProjectsManager.save_projects(projects)

    @staticmethod
    def unlink_project(cwd: Optional[Path] = None):
        """
        Unlink current directory from project.

        Args:
            cwd: Directory path (defaults to current directory)
        """
        if cwd is None:
            cwd = Path.cwd()

        cwd_str = str(cwd.resolve())
        projects = ProjectsManager.load_projects()

        if cwd_str in projects:
            del projects[cwd_str]
            ProjectsManager.save_projects(projects)

    @staticmethod
    def list_linked_projects() -> dict:
        """
        List all linked projects.

        Returns:
            Dict mapping directory paths to project info
        """
        return ProjectsManager.load_projects()
