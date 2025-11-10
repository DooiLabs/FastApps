"""Tests for the FastApps init CLI command."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from fastapps.cli.commands import create as create_module
from fastapps.cli.commands import init as init_module


@pytest.fixture(autouse=True)
def stub_create_widget(monkeypatch):
    """Stub widget creation to avoid heavy work during init tests."""

    monkeypatch.setattr(create_module, "create_widget", lambda *args, **kwargs: None)
    yield


@pytest.fixture
def stub_subprocess_run(monkeypatch):
    """Stub subprocess.run used for npm install to avoid external calls."""

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(init_module.subprocess, "run", _fake_run)
    yield


def test_init_project_invokes_uv_wrapper(monkeypatch, tmp_path, stub_subprocess_run):
    """Ensure init_project routes uv calls through run_uv_command."""

    call_log: list[tuple[tuple[str, ...], Path]] = []

    def _fake_run_uv(args, cwd=None):
        call_log.append((tuple(args), Path(cwd) if cwd else None))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(init_module, "run_uv_command", _fake_run_uv)
    monkeypatch.setattr(init_module, "get_cli_version", lambda: "9.9.9")
    monkeypatch.chdir(tmp_path)

    assert init_module.init_project("demo") is True

    assert [entry[0] for entry in call_log] == [
        ("init", "--bare", "demo"),
        ("add", "fastapps>=9.9.9"),
    ]
    assert call_log[0][1].resolve() == tmp_path
    assert call_log[1][1].resolve() == (tmp_path / "demo").resolve()


def test_init_project_handles_missing_uv(monkeypatch, tmp_path):
    """init_project should fail gracefully when uv isn't available."""

    def _fake_run_uv(args, cwd=None):
        raise FileNotFoundError("uv not installed")

    monkeypatch.setattr(init_module, "run_uv_command", _fake_run_uv)
    monkeypatch.chdir(tmp_path)

    assert init_module.init_project("demo") is False
    assert not (tmp_path / "demo").exists()


def test_init_project_creates_expected_structure(
    monkeypatch, tmp_path, stub_subprocess_run
):
    """Full init run should create the expected project layout."""

    monkeypatch.setattr(
        init_module,
        "run_uv_command",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )
    monkeypatch.setattr(init_module, "get_cli_version", lambda: "2.0.0")
    monkeypatch.chdir(tmp_path)

    assert init_module.init_project("demo") is True

    project_dir = tmp_path / "demo"
    assert project_dir.exists()
    assert (project_dir / "server" / "main.py").exists()
    assert (project_dir / "server" / "tools").is_dir()
    assert (project_dir / "server" / "api" / "__init__.py").exists()
    assert (project_dir / "widgets").is_dir()
    assert (project_dir / "package.json").exists()
    assert (project_dir / "README.md").read_text().startswith("# demo")
    assert (project_dir / ".gitignore").exists()


def test_init_project_respects_python_version(
    monkeypatch, tmp_path, stub_subprocess_run
):
    """Passing --python-version should be forwarded to uv init."""

    call_log: list[tuple[str, ...]] = []

    def _fake_run_uv(args, cwd=None):
        call_log.append(tuple(args))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(init_module, "run_uv_command", _fake_run_uv)
    monkeypatch.setattr(init_module, "get_cli_version", lambda: "1.0.0")
    monkeypatch.chdir(tmp_path)

    assert init_module.init_project("demo", python_version="3.11") is True

    assert call_log[0] == ("init", "--bare", "demo", "--python", "3.11")
