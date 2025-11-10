import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class WidgetBuildResult:
    """Result of building a widget."""

    name: str
    hash: str
    html: str


class WidgetBuilder:
    """
    Widget builder for Flick framework.

    Discovers widgets, builds them with Vite, and parses the results.
    """

    def __init__(self, project_root: Path | str):
        self.project_root = (
            Path(project_root) if isinstance(project_root, str) else project_root
        )
        self.assets_dir = self.project_root / "assets"
        self.widgets_dir = self.project_root / "widgets"
        self.framework_dir = Path(__file__).parent

    def build_all(self, mode: str = "hosted") -> Dict[str, WidgetBuildResult]:
        """
        Build all widgets in the project.

        Args:
            mode: Build mode - "hosted" (default, external JS/CSS references) or
                  "inline" (self-contained HTML)

        Returns:
            Dictionary mapping widget names to build results.
        """
        # 1. Auto-discover widgets
        self._discover_widgets()

        # 2. Ensure unified build script exists in project (if not exists)
        self._ensure_build_script()

        # 3. Run build (Windows-compatible)
        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
        build_script = "build-all.mts"

        # Pass mode and asset URLs via environment
        env = os.environ.copy()
        # Explicit mode for the script
        env["MODE"] = mode
        if mode == "hosted":
            # Use PUBLIC_URL if available (for absolute URLs in iframes)
            # Otherwise fall back to relative /assets path
            public_url = env.get("PUBLIC_URL", "")
            if public_url:
                env["BASE_URL"] = f"{public_url}/assets"
            else:
                env["BASE_URL"] = "/assets"

        subprocess.run(
            [npx_cmd, "tsx", build_script],
            cwd=self.project_root,
            check=True,
            env=env
        )

        # 4. Parse results
        return self._parse_build_results()

    def _ensure_build_script(self):
        """
        Ensure build script exists.

        Args:
            mode: Build mode - determines which script to copy
        """
        # Use unified build script name
        script_name = "build-all.mts"

        project_build_script = self.project_root / script_name
        framework_build_script = self.framework_dir / script_name

        # Copy from framework if not exists
        if not project_build_script.exists():
            if framework_build_script.exists():
                shutil.copy(framework_build_script, project_build_script)
                print(f"Copied {script_name} from FastApps framework")
            else:
                # Fallback: check node_modules
                node_modules_script = (
                    self.project_root / "node_modules" / "fastapps" / script_name
                )
                if node_modules_script.exists():
                    shutil.copy(node_modules_script, project_build_script)
                    print(f"Copied {script_name} from fastapps package")
                else:
                    raise FileNotFoundError(
                        f"{script_name} not found. Please install fastapps: npm install --save-dev fastapps"
                    )

    def _discover_widgets(self):
        """
        Discover widgets in the widgets directory.

        Mounting logic is automatically injected during build,
        so each widget only needs an index.jsx file!
        """
        widget_count = 0
        for widget_dir in self.widgets_dir.iterdir():
            if not widget_dir.is_dir() or widget_dir.name.startswith("."):
                continue

            widget_name = widget_dir.name
            index_file = widget_dir / "index.jsx"

            if index_file.exists():
                widget_count += 1
                print(f"Found widget: {widget_name}")

        if widget_count > 0:
            print(f"\nReady to build {widget_count} widget(s)")

    def _parse_build_results(self) -> Dict[str, WidgetBuildResult]:
        """Parse built widget HTML files."""
        results = {}
        for html_file in self.assets_dir.glob("*-*.html"):
            match = re.match(r"(.+)-([0-9a-f]{4})\.html$", html_file.name)
            if match:
                name, hash_val = match.groups()
                results[name] = WidgetBuildResult(
                    name=name, hash=hash_val, html=html_file.read_text()
                )
        return results
