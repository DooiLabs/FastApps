"""Artifact packaging for FastApps deployment."""

import json
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapps.core.utils import get_cli_version

class ArtifactPackager:
    """Packages FastApps project for deployment."""

    def __init__(self, project_root: Path):
        """
        Initialize artifact packager.

        Args:
            project_root: Root directory of FastApps project
        """
        self.project_root = project_root

    def package(self) -> Path:
        """
        Create deployment package as tar.gz.

        Returns:
            Path to created tarball

        Raises:
            FileNotFoundError: If required files/directories are missing
            RuntimeError: If packaging fails
        """
        import shutil

        # Validate project structure
        self._validate_project()

        # Use TemporaryDirectory context manager for automatic cleanup
        with tempfile.TemporaryDirectory(prefix="fastapps-deploy-") as temp_dir_str:
            temp_dir = Path(temp_dir_str)

            try:
                # Create manifest
                manifest = self._create_manifest()
                manifest_path = temp_dir / ".fastapps-manifest.json"
                manifest_path.write_text(json.dumps(manifest, indent=2))

                # Create tarball in temp directory
                tarball_temp_path = temp_dir / "deployment.tar.gz"

                with tarfile.open(tarball_temp_path, "w:gz") as tar:
                    # Add manifest
                    tar.add(
                        manifest_path,
                        arcname=".fastapps-manifest.json",
                    )

                    # Add required directories and files
                    self._add_directory(tar, "assets")
                    self._add_directory(tar, "server")

                    # Add configuration files
                    self._add_file(tar, "package.json")
                    self._add_file(tar, "requirements.txt")

                    # Add optional files if they exist
                    for optional_file in ["README.md", ".env.example"]:
                        optional_path = self.project_root / optional_file
                        if optional_path.exists():
                            tar.add(optional_path, arcname=optional_file)

                # Move tarball to project root with timestamp
                from datetime import datetime

                timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
                final_path = self.project_root / f".fastapps-deploy-{timestamp}.tar.gz"
                shutil.move(str(tarball_temp_path), str(final_path))

                return final_path

            except Exception as e:
                # TemporaryDirectory cleanup is automatic via context manager
                raise RuntimeError(f"Failed to create deployment package: {e}")

    def _validate_project(self):
        """
        Validate that project has required structure.

        Raises:
            FileNotFoundError: If required files are missing
        """
        required_dirs = ["assets", "server"]
        required_files = ["package.json", "requirements.txt", "server/main.py"]

        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                raise FileNotFoundError(
                    f"Required directory '{dir_name}' not found. "
                    f"Make sure you're in a FastApps project root."
                )

        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required file '{file_name}' not found. "
                    f"Make sure you're in a FastApps project root."
                )

    def _create_manifest(self) -> Dict:
        """
        Create deployment manifest with project metadata.

        Returns:
            Manifest dictionary
        """
        return {
            "fastapps_version": get_cli_version(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "project_name": self._get_project_name(),
            "widgets": self._list_widgets(),
            "dependencies": {
                "python": self._parse_python_dependencies(),
                "node": self._parse_node_dependencies(),
            },
        }

    def _get_project_name(self) -> str:
        """
        Extract project name from package.json.

        Returns:
            Project name or 'unknown'
        """
        try:
            package_json_path = self.project_root / "package.json"
            package_data = json.loads(package_json_path.read_text())
            return package_data.get("name", "unknown")
        except Exception:
            return "unknown"

    def _list_widgets(self) -> List[str]:
        """
        List all built widget identifiers.

        Returns:
            List of widget identifiers
        """
        widgets = []
        assets_dir = self.project_root / "assets"

        if assets_dir.exists():
            for html_file in assets_dir.glob("*.html"):
                # Extract widget identifier from filename
                # Format: widgetid-hash.html
                filename = html_file.stem
                if "-" in filename:
                    widget_id = filename.rsplit("-", 1)[0]
                    widgets.append(widget_id)

        return sorted(set(widgets))

    def _parse_python_dependencies(self) -> List[str]:
        """
        Parse Python dependencies from requirements.txt.

        Returns:
            List of package specifications
        """
        try:
            requirements_path = self.project_root / "requirements.txt"
            requirements_text = requirements_path.read_text()

            dependencies = []
            for line in requirements_text.splitlines():
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    dependencies.append(line)

            return dependencies
        except Exception:
            return []

    def _parse_node_dependencies(self) -> Dict[str, str]:
        """
        Parse Node.js dependencies from package.json.

        Returns:
            Dictionary of package name to version
        """
        try:
            package_json_path = self.project_root / "package.json"
            package_data = json.loads(package_json_path.read_text())
            return package_data.get("dependencies", {})
        except Exception:
            return {}

    def _add_directory(self, tar: tarfile.TarFile, dir_name: str):
        """
        Add directory to tarball with exclusions.

        Args:
            tar: TarFile object
            dir_name: Directory name relative to project root
        """
        dir_path = self.project_root / dir_name

        if not dir_path.exists():
            return

        # Exclusion patterns
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "*.swp",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".git",
        ]

        def should_exclude(path: Path) -> bool:
            """Check if path matches exclusion patterns."""
            path_str = str(path)
            for pattern in exclude_patterns:
                if pattern in path_str:
                    return True
            return False

        # Add directory recursively with exclusions
        for item in dir_path.rglob("*"):
            if should_exclude(item):
                continue

            # Calculate relative path for archive
            rel_path = item.relative_to(self.project_root)

            tar.add(item, arcname=str(rel_path))

    def _add_file(self, tar: tarfile.TarFile, file_name: str):
        """
        Add single file to tarball.

        Args:
            tar: TarFile object
            file_name: File name relative to project root
        """
        file_path = self.project_root / file_name

        if file_path.exists():
            tar.add(file_path, arcname=file_name)
