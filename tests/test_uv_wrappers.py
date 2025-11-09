"""Tests for uv wrapper helpers in fastapps.core.utils."""

from types import SimpleNamespace
import subprocess

import pytest

from fastapps.core import utils as core_utils


def test_is_uv_installed_uses_wrapper(monkeypatch):
    """Wrapper call should be delegated to run_uv_command."""

    captured = {}

    def _fake_run_uv(args, cwd=None):
        captured["args"] = args
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(core_utils, "run_uv_command", _fake_run_uv)

    assert core_utils.is_uv_installed() is True
    assert captured["args"] == ["--version"]


def test_is_uv_installed_handles_errors(monkeypatch):
    """is_uv_installed should fall back to False when uv check fails."""

    def _fake_run_uv(args, cwd=None):
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(core_utils, "run_uv_command", _fake_run_uv)

    assert core_utils.is_uv_installed() is False


def test_is_package_installed_uses_wrapper(monkeypatch):
    """Package detection should rely on run_uv_command."""

    recorded: list[list[str]] = []

    def _fake_run_uv(args, cwd=None):
        recorded.append(args)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(core_utils, "run_uv_command", _fake_run_uv)

    assert core_utils.is_package_installed("foo") is True
    assert recorded == [["pip", "show", "foo"]]


def test_is_package_installed_handles_errors(monkeypatch):
    """Failed uv execution should be treated as missing package."""

    def _fake_run_uv(args, cwd=None):
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(core_utils, "run_uv_command", _fake_run_uv)

    assert core_utils.is_package_installed("foo") is False
