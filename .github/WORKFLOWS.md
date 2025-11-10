# GitHub Workflows Documentation

This directory contains automated workflows for the FastApps project.

## Workflows Overview

### 1. CI Pipeline (`ci.yml`)
**Triggers**: Push/PR to main or develop branches

**Jobs**:
- **Test**: Runs tests on multiple OS (Ubuntu, macOS, Windows) and Python versions (3.11, 3.12)
  - Runs pytest with coverage
  - Uploads coverage to Codecov
- **Lint**: Checks code formatting with Black and lints with Ruff
- **Type Check**: Runs mypy for type checking
- **Build**: Builds the package and validates it with twine

### 2. PyPI Publishing (`publish.yml`)
**Triggers**: GitHub release is published

**Actions**:
- Builds the package
- Publishes to PyPI using API token
- Requires `PYPI_API_TOKEN` secret

### 3. Test PyPI Publishing (`test-publish.yml`)
**Triggers**: GitHub release is created (draft)

**Actions**:
- Builds the package
- Publishes to Test PyPI for validation
- Requires `TEST_PYPI_API_TOKEN` secret

### 4. Dependency Review (`dependency-review.yml`)
**Triggers**: Pull requests to main

**Actions**:
- Reviews dependencies for security vulnerabilities
- Fails on moderate or higher severity issues

### 5. CodeQL Analysis (`codeql.yml`)
**Triggers**:
- Push to main
- Pull requests to main
- Weekly schedule (Mondays)

**Actions**:
- Scans code for security vulnerabilities
- Analyzes Python codebase
- Reports findings to GitHub Security

### 6. Release Drafter (`release-drafter.yml`)
**Triggers**: Push to main

**Actions**:
- Automatically drafts release notes
- Categorizes changes by labels
- Suggests version bumps based on labels

## Setup Requirements

### Required Secrets

Add these secrets in GitHub Settings → Secrets and variables → Actions:

1. **PYPI_API_TOKEN**
   - Get from: https://pypi.org/manage/account/token/
   - Scope: Entire account or specific to fastapps
   - Used by: `publish.yml`

2. **TEST_PYPI_API_TOKEN** (Optional)
   - Get from: https://test.pypi.org/manage/account/token/
   - Used by: `test-publish.yml`
   - Useful for testing releases before production

### Codecov Integration (Optional)

1. Sign up at https://codecov.io
2. Connect your GitHub repository
3. Token is automatically provided by GitHub Actions

## Release Process

### Standard Release Flow

1. **Develop** → Merge features into `develop` branch
   - CI runs on every commit
   - Tests must pass

2. **Prepare Release**
   - Update version in `pyproject.toml` and `setup.py`
   - Merge `develop` → `main`
   - Release Drafter creates draft release notes

3. **Create Release**
   - Go to Releases → Edit draft
   - Review and edit release notes
   - Create tag (e.g., `v1.0.9`)
   - Publish release

4. **Automatic Publishing**
   - `publish.yml` triggers on release publish
   - Package builds and publishes to PyPI
   - Users can install with `pip install fastapps` or `uv pip install fastapps`

### Testing Releases (Optional)

Before publishing to production PyPI:

1. Create a **draft** release
2. `test-publish.yml` publishes to Test PyPI
3. Test installation: `pip install -i https://test.pypi.org/simple/ fastapps` or `uv pip install --index-url https://test.pypi.org/simple/ fastapps`
4. If successful, publish the release

## PR Labels for Release Notes

Use these labels on pull requests for automatic categorization:

- `feature`, `enhancement` → 🚀 Features
- `fix`, `bugfix`, `bug` → 🐛 Bug Fixes
- `chore`, `dependencies` → 🧰 Maintenance
- `documentation`, `docs` → 📚 Documentation

Version bump labels:
- `major` → Breaking changes (1.0.0 → 2.0.0)
- `minor`, `feature` → New features (1.0.0 → 1.1.0)
- `patch`, `fix` → Bug fixes (1.0.0 → 1.0.1)

## Dependabot

Configured in `.github/dependabot.yml`:
- Updates GitHub Actions weekly
- Updates Python dependencies weekly
- Automatically creates PRs for updates

## Running Tests Locally

```bash
# Install dev dependencies (recommended - matches CI)
uv sync --dev

# Or with pip (traditional)
# pip install -e ".[dev]"

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=fastapps --cov-report=html

# Format code
uv run black .

# Lint code
uv run ruff check .

# Build package
uv run python -m build

# Check package
uv run twine check dist/*
```

## Troubleshooting

### CI Failures

**Tests fail**:
- Check test output in GitHub Actions logs
- Run tests locally: `uv run pytest -v`

**Linting fails**:
- Run `uv run black .` to auto-format
- Run `uv run ruff check .` to see issues

**Build fails**:
- Ensure `pyproject.toml` is valid
- Check dependencies are correct

### Publishing Failures

**PyPI upload fails**:
- Verify `PYPI_API_TOKEN` is set correctly
- Ensure version number is unique (not already published)
- Check package name isn't taken

**Test PyPI works but production fails**:
- Version might already exist on PyPI
- Token might have wrong permissions

## Badge Examples

Add to your README.md:

```markdown
[![CI](https://github.com/fastapps-framework/fastapps/actions/workflows/ci.yml/badge.svg)](https://github.com/fastapps-framework/fastapps/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/fastapps-framework/fastapps/branch/main/graph/badge.svg)](https://codecov.io/gh/fastapps-framework/fastapps)
[![PyPI version](https://badge.fury.io/py/fastapps.svg)](https://badge.fury.io/py/fastapps)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastapps.svg)](https://pypi.org/project/fastapps/)
```
