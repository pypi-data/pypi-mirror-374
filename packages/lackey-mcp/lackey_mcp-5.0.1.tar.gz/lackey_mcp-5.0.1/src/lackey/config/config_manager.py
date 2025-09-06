"""Configuration management for Lackey."""

import configparser
from pathlib import Path
from typing import Optional


class LackeyConfig:
    """Manages Lackey configuration from lackey.config file."""

    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize config manager.

        Args:
            workspace_root: Path to workspace root. If None, searches for
                .lackey directory.
        """
        self.workspace_root = self._find_workspace_root(workspace_root)
        self.config_path = self.workspace_root / "lackey.config"
        self.config = configparser.ConfigParser()
        self._load_config()

    def _find_workspace_root(self, workspace_root: Optional[str]) -> Path:
        """Find the workspace root containing .lackey directory."""
        if workspace_root:
            return Path(workspace_root)

        # Search upward from current directory for .lackey
        current = Path.cwd()
        while current != current.parent:
            if (current / ".lackey").exists():
                return current
            current = current.parent

        # Default to current directory
        return Path.cwd()

    def _load_config(self) -> None:
        """Load configuration from lackey.config file."""
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            # Set defaults if no config file exists
            self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default configuration values."""
        if not self.config.has_section("aws"):
            self.config.add_section("aws")
        self.config.set("aws", "credentials_profile", "lackey")

        if not self.config.has_section("general"):
            self.config.add_section("general")
        self.config.set("general", "log_level", "INFO")

    def get_aws_profile(self) -> str:
        """Get AWS credentials profile name."""
        return self.config.get("aws", "credentials_profile", fallback="lackey")

    def get_log_level(self) -> str:
        """Get log level."""
        return self.config.get("general", "log_level", fallback="INFO")

    def create_default_config(self) -> None:
        """Create default lackey.config file."""
        self._set_defaults()

        with open(self.config_path, "w") as f:
            f.write(
                """[aws]
# AWS credentials profile to use for all Lackey operations
# This should match a profile name in your ~/.aws/credentials file
credentials_profile = lackey

[general]
# General Lackey configuration options
log_level = INFO
"""
            )

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, "w") as f:
            self.config.write(f)


# Global config instance
_config_instance = None


def get_config() -> LackeyConfig:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = LackeyConfig()
    return _config_instance
