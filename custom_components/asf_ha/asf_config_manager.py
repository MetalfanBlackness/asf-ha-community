"""ASF configuration file manager.

This module handles the creation, reading, and updating of ASF configuration files
within the Home Assistant configuration directory structure.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    DEFAULT_CONFIG_PATH,
    CONF_ASF_CONFIG_PATH,
)
from .utils import (
    get_config_path,
    get_asf_config_file,
    get_logs_dir,
    get_plugins_dir,
    validate_config_path,
)

_LOGGER = logging.getLogger(__name__)

# Default ASF configuration template
DEFAULT_ASF_CONFIG = {
    "SteamOwnerID": None,
    "CurrentCulture": "en-US",
    "Bots": [],
    "Database": {
        "Provider": "SQLite",
        "ConnectionString": "Data Source=ASF.db"
    },
    "IPC": {
        "Enabled": True,
        "Host": "0.0.0.0",
        "Port": 1242,
        "Password": ""
    },
    "Logging": {
        "Level": "Debug",
        "Output": "File",
        "FilePath": "logs/ASF.log",
        "MaxSize": 10,
        "MaxFiles": 5
    },
    "Plugins": {
        "Enabled": True,
        "Directories": ["plugins"]
    },
    "Web": {
        "Enabled": True,
        "Host": "0.0.0.0",
        "Port": 1242,
        "Password": ""
    }
}


class ASFConfigManager:
    """Manager for ASF configuration files."""

    def __init__(self, hass: HomeAssistant, entry_data: dict[str, Any]):
        """Initialize the config manager."""
        self.hass = hass
        self.entry_data = entry_data
        self._config_path = get_config_path(hass, entry_data)
        self._config_file = get_asf_config_file(hass, entry_data)
        self._logs_dir = get_logs_dir(hass, entry_data)
        self._plugins_dir = get_plugins_dir(hass, entry_data)

    @property
    def config_path(self) -> Path:
        """Get the ASF configuration directory path."""
        return self._config_path

    @property
    def config_file(self) -> Path:
        """Get the ASF configuration file path."""
        return self._config_file

    @property
    def logs_dir(self) -> Path:
        """Get the ASF logs directory path."""
        return self._logs_dir

    @property
    def plugins_dir(self) -> Path:
        """Get the ASF plugins directory path."""
        return self._plugins_dir

    def config_exists(self) -> bool:
        """Check if ASF configuration file exists."""
        return self._config_file.exists()

    def create_default_config(self, owner_id: str | None = None) -> dict[str, Any]:
        """Create a default ASF configuration file.
        
        Args:
            owner_id: Steam owner ID to use in configuration
            
        Returns:
            The created configuration dictionary
        """
        config = DEFAULT_ASF_CONFIG.copy()
        
        if owner_id:
            config["SteamOwnerID"] = owner_id
        
        # Update paths to use relative paths from config directory
        config["Logging"]["FilePath"] = f"logs/ASF.log"
        config["Database"]["ConnectionString"] = f"Data Source={self._config_path / 'ASF.db'}"
        config["Plugins"]["Directories"] = [f"plugins"]
        
        # Write the configuration file
        self._write_config(config)
        
        _LOGGER.info(f"Created default ASF configuration at: {self._config_file}")
        
        return config

    def read_config(self) -> dict[str, Any] | None:
        """Read the ASF configuration file.
        
        Returns:
            The configuration dictionary, or None if file doesn't exist
        """
        if not self.config_exists():
            _LOGGER.warning(f"ASF configuration file not found: {self._config_file}")
            return None
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Invalid JSON in ASF configuration: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Error reading ASF configuration: {e}")
            return None

    def update_config(self, updates: dict[str, Any]) -> bool:
        """Update the ASF configuration file.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self.config_exists():
            _LOGGER.error(f"Cannot update non-existent configuration: {self._config_file}")
            return False
        
        try:
            config = self.read_config()
            if config is None:
                return False
            
            # Apply updates
            config.update(updates)
            
            # Write back to file
            self._write_config(config)
            
            _LOGGER.info(f"Updated ASF configuration at: {self._config_file}")
            return True
        except Exception as e:
            _LOGGER.error(f"Error updating ASF configuration: {e}")
            return False

    def _write_config(self, config: dict[str, Any]) -> None:
        """Write configuration to file.
        
        Args:
            config: Configuration dictionary to write
        """
        # Ensure parent directories exist
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with pretty formatting
        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def add_bot(self, bot_config: dict[str, Any]) -> bool:
        """Add a bot to the ASF configuration.
        
        Args:
            bot_config: Bot configuration dictionary
            
        Returns:
            True if bot was added successfully, False otherwise
        """
        if not self.config_exists():
            self.create_default_config()
        
        try:
            config = self.read_config()
            if config is None:
                return False
            
            # Add or update bot
            bots = config.get("Bots", [])
            bot_name = bot_config.get("SteamLogin")
            
            # Check if bot already exists
            existing_index = None
            for i, bot in enumerate(bots):
                if bot.get("SteamLogin") == bot_name:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing bot
                bots[existing_index].update(bot_config)
            else:
                # Add new bot
                bots.append(bot_config)
            
            config["Bots"] = bots
            self._write_config(config)
            
            _LOGGER.info(f"Added/updated bot: {bot_name}")
            return True
        except Exception as e:
            _LOGGER.error(f"Error adding bot: {e}")
            return False

    def remove_bot(self, bot_name: str) -> bool:
        """Remove a bot from the ASF configuration.
        
        Args:
            bot_name: Name of the bot to remove
            
        Returns:
            True if bot was removed successfully, False otherwise
        """
        if not self.config_exists():
            return False
        
        try:
            config = self.read_config()
            if config is None:
                return False
            
            bots = config.get("Bots", [])
            config["Bots"] = [bot for bot in bots if bot.get("SteamLogin") != bot_name]
            
            self._write_config(config)
            
            _LOGGER.info(f"Removed bot: {bot_name}")
            return True
        except Exception as e:
            _LOGGER.error(f"Error removing bot: {e}")
            return False

    def validate_config_path(self) -> bool:
        """Validate the configuration path.
        
        Returns:
            True if path is valid, False otherwise
        """
        config_subdir = self.entry_data.get(CONF_ASF_CONFIG_PATH, DEFAULT_CONFIG_PATH)
        return validate_config_path(config_subdir) is not None


async def async_get_config_manager(hass: HomeAssistant, entry_data: dict[str, Any]) -> ASFConfigManager:
    """Get or create an ASF config manager.
    
    Args:
        hass: Home Assistant instance
        entry_data: Configuration entry data
        
    Returns:
        ASFConfigManager instance
    """
    return ASFConfigManager(hass, entry_data)
