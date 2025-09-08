"""
Configuration module for Taskinator.

This module provides a unified configuration interface for Taskinator.
It integrates the general configuration utilities with plugin-specific configurations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import dotenv
from rich.console import Console

# Import existing configuration utilities
from taskinator.utils.config import (
    DEFAULT_CONFIG,
    get_config as get_utils_config,
    get_config_value,
    get_project_path,
    get_tasks_dir,
    get_tasks_path,
    load_config as load_utils_config,
)

console = Console()


class Config:
    """
    Configuration manager for Taskinator.
    
    This class provides a unified interface for managing configuration settings
    across different components of Taskinator, including plugins and core functionality.
    
    It supports:
    - Loading and saving configuration from/to a JSON file
    - Environment variable integration
    - Default values with override capability
    - Project-specific configurations
    
    Usage:
        config = Config(project_directory)
        config.set("sync.nextcloud.host", "https://nextcloud.example.com")
        host = config.get("sync.nextcloud.host")
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            project_directory: The project directory to use for configuration files.
                              If None, the current working directory is used.
        """
        self.project_directory = project_directory or os.getcwd()
        self.config_dir = os.path.join(self.project_directory, ".taskinator")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._config = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load environment variables
        dotenv.load_dotenv()
        
        # Load configuration if it exists
        self.reload()

    def reload(self):
        """Reload configuration from environment and config files."""
        # Start with default configuration
        self._config = load_utils_config()
        
        # Load configuration from .taskinator/config.json if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
            except Exception as e:
                console.print(
                    f"[WARNING] Error loading configuration from {self.config_file}: {str(e)}",
                    style="bold yellow",
                )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        # Handle nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            value = self._config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        # Handle simple keys
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Configuration value
        """
        # Handle nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            config = self._config
            
            # Navigate to the correct nested dictionary
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                elif not isinstance(config[part], dict):
                    config[part] = {}
                config = config[part]
                
            # Set the value in the nested dictionary
            config[parts[-1]] = value
        else:
            # Set the value directly
            self._config[key] = value

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            console.print(
                f"[INFO] Configuration saved to {self.config_file}",
                style="blue",
            )
        except Exception as e:
            console.print(
                f"[ERROR] Failed to save configuration to {self.config_file}: {str(e)}",
                style="bold red",
            )

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Dict[str, Any]: All configuration values
        """
        return self._config.copy()


# Provide backward compatibility with the utils.config module
def get_config() -> Dict[str, Any]:
    """Get configuration dictionary.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return Config().get_all()


def load_config() -> Dict[str, Any]:
    """Load configuration.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return Config().get_all()
