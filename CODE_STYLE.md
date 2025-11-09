# Code Style Guide

This document describes the code style and formatting standards for the FastApps project.

## Python Code Style

### Tools

We use the following tools to maintain code quality:

#### 1. Black - Code Formatter

Black is the uncompromising Python code formatter. It reformats entire files in place according to the Black code style.

**Installation**:
```bash
uv pip install black
```

**Usage**:
```bash
# Format all files
uv run black .

# Check formatting without changing files
uv run black --check .

# Format specific file
uv run black path/to/file.py
```

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

**Key Features**:
- Line length: 88 characters
- Double quotes for strings
- Trailing commas in multi-line structures
- Consistent indentation (4 spaces)

#### 2. Ruff - Fast Python Linter

Ruff is an extremely fast Python linter that replaces multiple tools (Flake8, isort, etc.).

**Installation**:
```bash
uv pip install ruff
```

**Usage**:
```bash
# Lint all files
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Lint specific file
uv run ruff check path/to/file.py
```

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

# Enable specific rule sets
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort (import sorting)
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]

# Ignore specific rules
ignore = [
    "E501",  # line too long (handled by Black)
    "B008",  # function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__
```

**Checked Rules**:
- **E/W**: PEP 8 style errors and warnings
- **F**: Logical errors (undefined names, unused imports)
- **I**: Import sorting and organization
- **C**: List/dict/set comprehension improvements
- **B**: Common bugs and design problems

#### 3. pytest - Testing

**Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--strict-markers",
    "--disable-warnings",
]
```

**Coverage** (`pyproject.toml`):
```toml
[tool.coverage.run]
source = ["fastapps"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Python Style Guidelines

### Imports

Always organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Ruff handles this automatically with the `I` rule set.

**Example**:
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Third-party
import httpx
from pydantic import BaseModel
from rich.console import Console

# Local
from fastapps.core.widget import Widget
from fastapps.auth.decorators import auth_required
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with `_` (single underscore)

**Example**:
```python
MAX_RETRIES = 3

class MyWidget(Widget):
    def process_data(self, input_data: Dict) -> Dict:
        _temp_value = self._calculate_internal()
        return {"result": _temp_value}

    def _calculate_internal(self) -> int:
        """Private helper method."""
        return 42
```

### Docstrings

Use Google-style docstrings for all public APIs:

```python
def create_widget(name: str, auth_type: str = None, scopes: list = None) -> bool:
    """Create a new widget with tool and component files.

    This function generates both the Python tool file and the React component
    file for a new widget, with optional authentication configuration.

    Args:
        name: Widget name (will be converted to proper formats)
        auth_type: Authentication type - 'required', 'none', or 'optional'.
            Defaults to None (inherits from server).
        scopes: List of OAuth scopes required for the widget.
            Only used when auth_type is 'required' or 'optional'.

    Returns:
        True if widget was created successfully, False if it already exists.

    Raises:
        ValueError: If name contains invalid characters.
        FileNotFoundError: If project structure is missing.

    Example:
        >>> create_widget("my-widget", auth_type="required", scopes=["user"])
        True
    """
    pass
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Dict, List, Optional, Any

def process_items(
    items: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, int]:
    """Process a list of items with optional configuration."""
    config = config or {}
    return {item: len(item) for item in items}
```

### String Formatting

Prefer f-strings for string formatting:

```python
# Good
name = "FastApps"
message = f"Welcome to {name}!"

# Avoid
message = "Welcome to %s!" % name
message = "Welcome to {}!".format(name)
```

**Note**: Be careful with nested f-strings in multi-line strings - extract to variables if needed:

```python
# Problematic
template = f"""
class {name}:
    value = "{f'nested {value}'}"  # Can cause parse errors
"""

# Better
nested_value = f"nested {value}"
template = f"""
class {name}:
    value = "{nested_value}"
"""
```

### Error Handling

Be specific with exception handling:

```python
# Good
try:
    result = process_data(data)
except ValueError as e:
    console.print(f"[red]Invalid data: {e}[/red]")
    return None
except KeyError as e:
    console.print(f"[red]Missing key: {e}[/red]")
    return None

# Avoid
try:
    result = process_data(data)
except Exception:
    pass
```

## JavaScript/React Code Style

For widget development:

### React Components

```jsx
// Functional components with hooks
import React from 'react';
import { useWidgetProps, useWidgetState } from 'fastapps';

export default function MyWidget() {
  const props = useWidgetProps();
  const [state, setState] = useWidgetState({ count: 0 });

  return (
    <div style={{
      padding: '20px',
      background: '#fff',
      borderRadius: '8px'
    }}>
      <h1>{props.message}</h1>
      <button onClick={() => setState({ count: state.count + 1 })}>
        Count: {state.count}
      </button>
    </div>
  );
}
```

### Styling

Prefer inline styles for widget components:
- Keeps widgets self-contained
- Avoids CSS conflicts
- Easier to theme dynamically

## CI/CD Integration

### GitHub Actions

Our CI pipeline automatically checks:

1. **Black formatting**:
   ```bash
   uv run black --check .
   ```

2. **Ruff linting**:
   ```bash
   uv run ruff check .
   ```

3. **Tests**:
   ```bash
   uv run pytest --cov=fastapps
   ```

4. **Type checking** (optional):
   ```bash
   uv run mypy fastapps --ignore-missing-imports
   ```

5. **Build validation**:
   ```bash
   python -m build
   twine check dist/*
   ```

### Pre-commit Hooks

Install pre-commit hooks to automatically format/lint before commits:

```bash
uv pip install pre-commit
uv run pre-commit install
```

`.pre-commit-config.yaml`:
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

## Editor Configuration

### VS Code

`.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm

1. **Black**:
   - Install Black: `uv pip install black`
   - Settings → Tools → Black → Enable
   - Settings → Tools → Actions on Save → Run Black

2. **Ruff**:
   - Install Ruff plugin from marketplace
   - Settings → Tools → Ruff → Enable

## Quick Reference

### Before Committing

```bash
# 1. Format code
uv run black .

# 2. Lint and auto-fix
uv run ruff check --fix .

# 3. Run tests
uv run pytest

# 4. Check coverage
uv run pytest --cov=fastapps --cov-report=term
```

### Common Issues

**"Black would reformat"**:
```bash
# Fix: Run Black
uv run black .
```

**"Ruff found issues"**:
```bash
# Try auto-fix first
uv run ruff check --fix .

# Then check remaining issues
uv run ruff check .
```

**"Import sorting"**:
```bash
# Ruff handles this automatically
uv run ruff check --fix .
```

## Resources

- **Black**: https://black.readthedocs.io/
- **Ruff**: https://docs.astral.sh/ruff/
- **PEP 8**: https://pep8.org/
- **Google Python Style**: https://google.github.io/styleguide/pyguide.html

---

Following these guidelines ensures consistent, high-quality code across the FastApps project.
