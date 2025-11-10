"""Tests for use command functionality."""

from unittest.mock import MagicMock, patch

from fastapps.cli.commands.use import use_metorial
from fastapps.core import utils as core_utils


def _setup_project(tmp_path, monkeypatch):
    """Create a minimal FastApps project structure under tmp_path and chdir there."""

    project_dir = tmp_path / "fastapps-project"
    api_dir = project_dir / "server" / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'fastapps-project'\nversion = '0.1.0'\n"
    )
    monkeypatch.chdir(project_dir)
    return project_dir


class TestUseCommand:
    """Tests for use command."""

    def test_use_metorial_creates_file(self, tmp_path, monkeypatch):
        """Test that use_metorial creates metorial_mcp.py file."""
        project_dir = _setup_project(tmp_path, monkeypatch)
        api_dir = project_dir / "server" / "api"
        metorial_file = api_dir / "metorial_mcp.py"

        with patch.object(core_utils, "safe_check_dependencies") as mock_check:
            mock_check.return_value = []
            with patch.object(core_utils, "run_uv_command") as mock_uv:
                result = use_metorial()
                mock_uv.assert_not_called()

            # Should succeed
            assert result is True

            # Verify file was created
            assert metorial_file.exists()

            # Verify file content
            content = metorial_file.read_text()
            assert "from metorial import Metorial" in content
            assert "from openai import AsyncOpenAI" in content
            assert "call_metorial" in content

    def test_use_metorial_checks_dependencies(self, tmp_path, monkeypatch):
        """Test that use_metorial calls dependency checking."""
        _setup_project(tmp_path, monkeypatch)
        with patch.object(core_utils, "safe_check_dependencies") as mock_check:
            mock_check.return_value = []

            result = use_metorial()

            assert result is True
            mock_check.assert_called_once_with(["metorial", "openai"])

    def test_use_metorial_fails_outside_project(self, tmp_path, monkeypatch):
        """Test that use_metorial fails outside FastApps project."""
        project_dir = tmp_path / "elsewhere"
        project_dir.mkdir()
        monkeypatch.chdir(project_dir)

        result = use_metorial()

        # Should fail
        assert result is False

    def test_use_metorial_requires_pyproject(self, tmp_path, monkeypatch):
        """Command should fail when pyproject.toml is missing."""
        project_dir = tmp_path / "fastapps-project"
        api_dir = project_dir / "server" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.chdir(project_dir)

        assert use_metorial() is False

    def test_use_metorial_installs_missing_packages(self, tmp_path, monkeypatch):
        """Missing deps should trigger uv add."""
        project_dir = _setup_project(tmp_path, monkeypatch)

        with patch.object(core_utils, "safe_check_dependencies") as mock_check:
            mock_check.return_value = ["metorial", "openai"]
            with patch.object(core_utils, "run_uv_command") as mock_uv:
                mock_uv.return_value = MagicMock()

                assert use_metorial() is True
                mock_uv.assert_called_once_with(
                    ["add", "metorial", "openai"], cwd=project_dir
                )
