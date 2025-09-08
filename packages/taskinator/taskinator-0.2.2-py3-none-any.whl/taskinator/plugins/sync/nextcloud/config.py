"""
Configuration for Nextcloud sync plugin.

This module provides configuration utilities for the Nextcloud sync plugin.
"""

import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NextcloudConfig(BaseModel):
    """Configuration for Nextcloud sync plugin."""

    host: str = Field(..., description="Nextcloud host URL")
    username: str = Field(..., description="Nextcloud username")
    password: Optional[str] = Field(None, description="Nextcloud password")
    app_token: Optional[str] = Field(None, description="Nextcloud app token")
    calendar_id: str = Field("personal", description="Calendar ID to use for tasks")
    sync_interval: int = Field(3600, description="Sync interval in seconds")
    auto_sync: bool = Field(False, description="Enable automatic sync")

    @classmethod
    def from_env(cls) -> "NextcloudConfig":
        """Create configuration from environment variables.

        Returns:
            NextcloudConfig: Configuration object
        """
        return cls(
            host=os.environ.get("NEXTCLOUD_HOST", ""),
            username=os.environ.get("NEXTCLOUD_USERNAME", ""),
            password=os.environ.get("NEXTCLOUD_PASSWORD"),
            app_token=os.environ.get("NEXTCLOUD_APP_TOKEN"),
            calendar_id=os.environ.get("NEXTCLOUD_CALENDAR_ID", "personal"),
            sync_interval=int(os.environ.get("NEXTCLOUD_SYNC_INTERVAL", "3600")),
            auto_sync=os.environ.get("NEXTCLOUD_AUTO_SYNC", "false").lower() == "true",
        )

    def to_env(self) -> Dict[str, str]:
        """Convert configuration to environment variables.

        Returns:
            Dict[str, str]: Environment variables
        """
        env = {
            "NEXTCLOUD_HOST": self.host,
            "NEXTCLOUD_USERNAME": self.username,
            "NEXTCLOUD_CALENDAR_ID": self.calendar_id,
            "NEXTCLOUD_SYNC_INTERVAL": str(self.sync_interval),
            "NEXTCLOUD_AUTO_SYNC": str(self.auto_sync).lower(),
        }

        if self.password:
            env["NEXTCLOUD_PASSWORD"] = self.password

        if self.app_token:
            env["NEXTCLOUD_APP_TOKEN"] = self.app_token

        return env

    def save_to_env_file(self, env_file: str = ".env") -> None:
        """Save configuration to .env file.

        Args:
            env_file: Path to .env file
        """
        # Read existing .env file
        env_vars = {}
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        # Update with Nextcloud config
        env_vars.update(self.to_env())

        # Write back to .env file
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")


def get_config() -> NextcloudConfig:
    """Get Nextcloud configuration from environment variables.

    Returns:
        NextcloudConfig: Configuration object
    """
    return NextcloudConfig.from_env()


def setup_config(
    host: str,
    username: str,
    password: Optional[str] = None,
    app_token: Optional[str] = None,
    calendar_id: str = "personal",
    sync_interval: int = 3600,
    auto_sync: bool = False,
    env_file: str = ".env",
) -> NextcloudConfig:
    """Set up Nextcloud configuration.

    Args:
        host: Nextcloud host URL
        username: Nextcloud username
        password: Nextcloud password
        app_token: Nextcloud app token
        calendar_id: Calendar ID to use for tasks
        sync_interval: Sync interval in seconds
        auto_sync: Enable automatic sync
        env_file: Path to .env file

    Returns:
        NextcloudConfig: Configuration object
    """
    # Create configuration
    config = NextcloudConfig(
        host=host,
        username=username,
        password=password,
        app_token=app_token,
        calendar_id=calendar_id,
        sync_interval=sync_interval,
        auto_sync=auto_sync,
    )

    # Save to .env file
    config.save_to_env_file(env_file)

    return config
