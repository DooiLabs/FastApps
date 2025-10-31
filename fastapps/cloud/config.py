"""Configuration management for FastApps Cloud."""

import json
import os
from pathlib import Path
from typing import Optional


class CloudConfig:
    """Manages FastApps Cloud configuration and authentication tokens."""

    # Default cloud server URL
    DEFAULT_CLOUD_URL = "https://cloud-api.dooi.app"

    @staticmethod
    def get_config_dir() -> Path:
        """Get FastApps config directory."""
        config_dir = Path.home() / ".fastapps"
        config_dir.mkdir(exist_ok=True)
        return config_dir

    @staticmethod
    def get_config_file() -> Path:
        """Get config file path."""
        return CloudConfig.get_config_dir() / "config.json"

    @staticmethod
    def load_config() -> dict:
        """Load configuration from file."""
        config_file = CloudConfig.get_config_file()
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_config(config: dict) -> bool:
        """Save configuration to file."""
        config_file = CloudConfig.get_config_file()
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            # Set restrictive permissions (owner read/write only)
            os.chmod(config_file, 0o600)
            return True
        except Exception:
            return False

    @staticmethod
    def get_cloud_url() -> str:
        """Get cloud server URL."""
        config = CloudConfig.load_config()
        return config.get("cloud_url", CloudConfig.DEFAULT_CLOUD_URL)

    @staticmethod
    def set_cloud_url(url: str):
        """Set cloud server URL."""
        config = CloudConfig.load_config()
        config["cloud_url"] = url
        CloudConfig.save_config(config)

    @staticmethod
    def get_token() -> Optional[str]:
        """Get stored authentication token."""
        config = CloudConfig.load_config()
        return config.get("cloud_token")

    @staticmethod
    def set_token(token: str):
        """Save authentication token."""
        config = CloudConfig.load_config()
        config["cloud_token"] = token
        CloudConfig.save_config(config)

    @staticmethod
    def clear_token():
        """Remove authentication token."""
        config = CloudConfig.load_config()
        if "cloud_token" in config:
            del config["cloud_token"]
            CloudConfig.save_config(config)

    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in."""
        return CloudConfig.get_token() is not None
