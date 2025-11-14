# Repository Guidelines

## Project Structure & Module Organization
Core server logic lives under `fastapps/` (e.g., `core/`, `auth/`, `cli/`, `builder/`); treat it as the Python package exported to PyPI. React widget templates, CLI assets, and TypeScript build scripts live in `fastapps/templates/` and `js/`. Tests are under `tests/` with mirrors of package modules plus integration samples. Distribution artifacts land in `dist/`, and packaging metadata sits beside `pyproject.toml` and `uv.lock`.

## Build, Test & Development Commands
Use uv to mirror CI: `uv sync --dev` installs runtime + dev deps. Run the CLI locally with `uv run fastapps dev` to boot the sample app and expose the `/mcp` endpoint. Validate packaging before release via `uv build` then `uv run twine check dist/*`. Continuous quality gates are `uv run black .` and `uv run ruff check --fix .`.

## Coding Style & Naming Conventions
Python code follows Black (88 cols, 4-space indent, double quotes) and Ruff (E/W/F/I/C/B rules); organize imports stdlib → third-party → local. Classes use `PascalCase`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`, and private helpers get a leading underscore. Widget frontends should remain functional React components, prefer hooks + inline styles, and keep component names aligned with their directory names.

## Testing Guidelines
Pytest is configured in `pyproject.toml` with strict markers and verbosity; invoke via `uv run pytest` for the full suite or `uv run pytest -m "not slow"` for faster cycles. Coverage expectations focus on the `fastapps` package (`coverage run --source fastapps`). Name tests `test_<feature>.py` and mark integration-heavy flows with `@pytest.mark.integration` to keep CI filters predictable.

## Commit & Pull Request Guidelines
Repository history favors short, imperative subject lines (e.g., `Align carousel template with OpenAI guidelines`). Keep commits narrowly scoped and include context about templates, CLI behavior, or builder assets when relevant. Pull requests should describe motivation, summarize code-level changes, link GitHub issues or discussion threads, and attach CLI/log outputs or screenshots for UI-affecting changes. Ensure PRs pass Black, Ruff, and Pytest before requesting review.

## Security & Configuration Tips
Never commit `.env` or Ngrok tokens; rely on `python-dotenv` locally and GitHub secrets in CI/CD. When exposing MCP endpoints, run tunnels via `uv run fastapps dev --host 0.0.0.0` and verify TLS-provided URLs before sharing. Rotate JWT/signing keys stored under `FastApps/auth` helpers whenever deploying shared agents.
