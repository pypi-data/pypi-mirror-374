"""
Configuration manager for agent-fetch.

Handles global configuration settings including default repository, branch,
and other user-configurable options.
"""

import os
import pathlib
from typing import Dict, Any, Optional
import yaml


class ConfigManager:
    """Manages global configuration settings for the agent-fetch."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the config manager with specified or default config directory.

        Args:
            config_dir: Custom config directory path. If None, uses default location.
        """
        if config_dir:
            self.config_dir = pathlib.Path(config_dir)
        else:
            self.config_dir = self._get_default_config_dir()

        self.config_file = self.config_dir / "config.yaml"
        self._ensure_config_dir_exists()

    @staticmethod
    def _get_default_config_dir() -> pathlib.Path:
        """Get the default configuration directory for the current platform.

        Returns:
            Path to the default config directory.
        """
        if os.name == "nt":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata:
                return pathlib.Path(appdata) / "agentfetch"
            else:
                raise OSError("APPDATA environment variable not found")
        else:  # Unix-like systems (Linux, macOS)
            home = os.getenv("HOME")
            if home:
                return pathlib.Path(home) / ".agentfetch"
            else:
                raise OSError("HOME environment variable not found")

    def _ensure_config_dir_exists(self) -> None:
        """Ensure the configuration directory exists, creating it if necessary."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create config directory {self.config_dir}: {e}")

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from the config file.

        Returns:
            Dictionary containing configuration values.

        Raises:
            OSError: If there are issues reading the config file.
            yaml.YAMLError: If the config file contains invalid YAML.
        """
        if not self.config_file.exists():
            return self._get_default_config()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}

                # Merge with defaults for any missing keys
                defaults = self._get_default_config()
                defaults.update(config)
                return defaults

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file {self.config_file}: {e}")
        except OSError as e:
            raise OSError(f"Failed to read config file {self.config_file}: {e}")

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to the config file.

        Args:
            config: Configuration dictionary to save.

        Raises:
            OSError: If there are issues writing to the config file.
            yaml.YAMLError: If the config cannot be serialized to YAML.
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to serialize config to YAML: {e}")
        except OSError as e:
            raise OSError(f"Failed to write config file {self.config_file}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key to retrieve.
            default: Default value if key is not found.

        Returns:
            The configuration value or default if not found.
        """
        config = self.load_config()
        return config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key to set.
            value: Value to set for the key.
        """
        config = self.load_config()
        config[key] = value
        self.save_config(config)

    def set_default_repo(self, repo_url: str) -> None:
        """Set the default repository URL.

        Args:
            repo_url: The GitHub repository URL to set as default.
        """
        self.set("default_repo", repo_url)

    def get_default_repo(self) -> Optional[str]:
        """Get the default repository URL.

        Returns:
            The default repository URL or None if not set.
        """
        return self.get("default_repo")

    def set_default_branch(self, branch: str) -> None:
        """Set the default branch.

        Args:
            branch: The branch name to set as default.
        """
        self.set("default_branch", branch)

    def get_default_branch(self) -> str:
        """Get the default branch.

        Returns:
            The default branch name.
        """
        return self.get("default_branch", "main")

    def show_config(self) -> Dict[str, Any]:
        """Get the current configuration for display.

        Returns:
            Dictionary of current configuration values.
        """
        return self.load_config()

    def get_config_path(self) -> pathlib.Path:
        """Get the path to the configuration file.

        Returns:
            Path to the configuration file.
        """
        return self.config_file

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get the default configuration values.

        Returns:
            Dictionary with default configuration values.
        """
        return {
            "default_branch": "main",
            "default_repo": "https://github.com/FreeMarketamilitia/awesome-agents-md",
        }
