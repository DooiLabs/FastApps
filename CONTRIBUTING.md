# Contributing to FastApps

Thank you for your interest in contributing to FastApps! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Formatting](#code-style-and-formatting)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Messages](#commit-messages)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- npm or yarn

### Initial Setup

**Recommended: Using uv (matches CI pipeline)**

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fastapps.git
cd fastapps

# Install uv if not already installed
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
uv sync --dev

# Install pre-commit hooks (already installed via uv sync --dev)
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=fastapps --cov-report=html

# Run specific test file
uv run pytest tests/test_widget.py

# Run with verbose output
uv run pytest -v
```

### Building the Package

```bash
# With uv (recommended)
uv build

# Check package validity
uv run twine check dist/*

# Or with pip/build (traditional)
# python -m build
# twine check dist/*
```

## Code Style and Formatting

FastApps follows strict code style guidelines to maintain consistency across the codebase.

### Python Code Style

We use the following tools for Python code:

#### Black - Code Formatter

[Black](https://black.readthedocs.io/) automatically formats your Python code.

**Configuration** (in `pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

**Usage**:
```bash
# Format all Python files
uv run black .

# Check without modifying
uv run black --check .

# Format specific file
uv run black fastapps/core/widget.py
```

#### Ruff - Linter

[Ruff](https://docs.astral.sh/ruff/) is a fast Python linter.

**Configuration** (in `pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]
```

**Usage**:
```bash
# Lint all files
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Lint specific file
uv run ruff check fastapps/core/widget.py
```

#### Type Checking (Optional)

We use mypy for type checking (not strictly enforced but encouraged):

```bash
# Install mypy
uv pip install mypy

# Run type checking
mypy fastapps --ignore-missing-imports
```

### JavaScript/React Code Style

For React components in the `widgets/` directory:

- Use ESLint and Prettier (configured in generated projects)
- Follow React best practices
- Use functional components with hooks
- Prefer inline styles for widgets

### Pre-Commit Hooks

We recommend using pre-commit hooks to automatically format and lint code:

```bash
# If you used uv sync --dev, pre-commit is already installed.
# Just install the git hooks:
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files

# If pre-commit is not installed (standalone installation):
# uv pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Follow the naming convention: `test_*.py`
- Use pytest fixtures for common setup
- Write both unit and integration tests

**Example test**:
```python
import pytest
from fastapps.core.widget import Widget


def test_widget_creation():
    """Test that a widget can be instantiated."""
    class TestWidget(Widget):
        def render(self):
            return {"message": "test"}

    widget = TestWidget()
    assert widget is not None
    assert widget.render() == {"message": "test"}
```

### Test Coverage

Aim for >80% test coverage for new code:

```bash
# Generate coverage report
pytest --cov=fastapps --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Running CI Checks Locally

Before submitting a PR, run all CI checks locally:

**With uv (matches CI exactly):**

```bash
# Install dependencies
uv sync --dev

# Format code
black .

# Lint code
ruff check .

# Run tests
pytest --cov=fastapps

# Build package
uv build

# Check package
uv run twine check dist/*
```

## Pull Request Process

### Before Submitting

1. **Create an issue** first (for features/major changes)
2. **Fork and branch**: Create a feature branch from `main`
3. **Write tests**: Add tests for new functionality
4. **Update docs**: Update relevant documentation
5. **Format code**: Run Black and Ruff
6. **Run tests**: Ensure all tests pass locally

### PR Guidelines

1. **One feature per PR**: Keep PRs focused and atomic
2. **Link issues**: Reference related issues in the PR description
3. **Add tests**: Include tests for bug fixes and new features
4. **Update CHANGELOG**: Add entry to `CHANGELOG.md` (if applicable)
5. **Clean commits**: Squash WIP commits before submitting

### PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines (Black + Ruff)
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass locally
- [ ] No breaking changes (or documented)
```

### Review Process

1. Automated CI checks must pass
2. At least one maintainer approval required
3. All review comments addressed
4. Branch up-to-date with `main`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
feat(widgets): add support for custom themes

# Bug fix
fix(cli): resolve path resolution issue on Windows

# Documentation
docs(readme): update installation instructions

# Breaking change
feat(api)!: change widget registration API

BREAKING CHANGE: Widget.register() now requires 'identifier' parameter
```

## Issue Guidelines

### Bug Reports

Include:
- FastApps version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces

**Template**:
```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
1. Step one
2. Step two
3. ...

**Expected behavior**
What should happen

**Environment**
- FastApps version:
- Python version:
- OS:

**Additional context**
Any other relevant information
```

### Feature Requests

Include:
- Use case / problem to solve
- Proposed solution
- Alternative solutions considered
- Willing to contribute? (Yes/No)

## Code Review Guidelines

### For Contributors

- Be receptive to feedback
- Respond to review comments promptly
- Ask questions if unclear
- Update PR based on feedback

### For Reviewers

- Be respectful and constructive
- Focus on code, not the person
- Explain reasoning for requested changes
- Approve when satisfied with changes

## Development Workflow

### Typical Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes
# ... edit files ...

# 3. Format code
black .

# 4. Lint code
uv run ruff check --fix .

# 5. Run tests
uv run pytest

# 6. Commit changes
git add .
git commit -m "feat: add my new feature"

# 7. Push to fork
git push origin feature/my-new-feature

# 8. Create pull request on GitHub
```

### Keeping Fork Updated

```bash
# Add upstream remote (once)
git remote add upstream https://github.com/fastapps-framework/fastapps.git

# Fetch upstream changes
git fetch upstream

# Update main branch
git checkout main
git merge upstream/main

# Rebase feature branch
git checkout feature/my-feature
git rebase main
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `setup.py`
2. Update `CHANGELOG.md`
3. Create GitHub release with tag `vX.Y.Z`
4. GitHub Actions automatically publishes to PyPI

## Documentation

### Code Documentation

- Use docstrings for all public classes and functions
- Follow Google-style docstrings

**Example**:
```python
def create_widget(name: str, auth_type: str = None) -> bool:
    """Create a new widget with tool and component files.

    Args:
        name: Widget name
        auth_type: Authentication type ('required', 'none', 'optional')

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If name is invalid
    """
    pass
```

### README and Guides

- Keep examples simple and working
- Test all code examples
- Update when API changes

## Getting Help

- **Documentation**: Check [docs](./docs/)
- **Issues**: Search existing issues
- **Discord**: Join our [Discord community](https://discord.gg/5cEy3Jqek3)
- **Discussions**: GitHub Discussions for questions

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FastApps! 🚀
