"""Utility functions for ArchiSteamFarm integration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import (
    DOMAIN,
    CONF_ASF_CONFIG_PATH,
    DEFAULT_CONFIG_PATH,
)


def get_config_path(hass: HomeAssistant, entry_data: dict[str, Any]) -> Path:
    """Get the absolute path for ASF configuration directory.
    
    Returns the config path within Home Assistant's config directory.
    
    Args:
        hass: Home Assistant instance
        entry_data: Configuration entry data
        
    Returns:
        Path to the ASF configuration directory
    """
    # Get the config path from entry data or use default
    config_subdir = entry_data.get(CONF_ASF_CONFIG_PATH, DEFAULT_CONFIG_PATH)
    
    # Get Home Assistant's config directory
    hass_config_dir = Path(hass.config.config_dir)
    
    # Create the full path
    asf_config_dir = hass_config_dir / config_subdir
    
    # Ensure the directory exists
    asf_config_dir.mkdir(parents=True, exist_ok=True)
    
    return asf_config_dir


def get_asf_config_file(hass: HomeAssistant, entry_data: dict[str, Any], filename: str = "ASF.json") -> Path:
    """Get the path to a specific ASF configuration file.
    
    Args:
        hass: Home Assistant instance
        entry_data: Configuration entry data
        filename: Name of the configuration file
        
    Returns:
        Path to the ASF configuration file
    """
    config_dir = get_config_path(hass, entry_data)
    return config_dir / filename


def get_logs_dir(hass: HomeAssistant, entry_data: dict[str, Any]) -> Path:
    """Get the path to the ASF logs directory.
    
    Args:
        hass: Home Assistant instance
        entry_data: Configuration entry data
        
    Returns:
        Path to the ASF logs directory
    """
    config_dir = get_config_path(hass, entry_data)
    logs_dir = config_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_plugins_dir(hass: HomeAssistant, entry_data: dict[str, Any]) -> Path:
    """Get the path to the ASF plugins directory.
    
    Args:
        hass: Home Assistant instance
        entry_data: Configuration entry data
        
    Returns:
        Path to the ASF plugins directory
    """
    config_dir = get_config_path(hass, entry_data)
    plugins_dir = config_dir / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    return plugins_dir


def validate_config_path(config_path: str) -> str | None:
    """Validate a configuration path.
    
    Args:
        config_path: The configuration path to validate
        
    Returns:
        The validated path, or None if invalid
    """
    if not config_path:
        return None
    
    # Check for path traversal attempts
    if ".." in config_path or config_path.startswith("/") or config_path.startswith("\\"):
        return None
    
    # Remove leading/trailing slashes
    config_path = config_path.strip("/\\")
    
    # Check if path contains only valid characters
    if not all(c.isalnum() or c in (".", "_", "-", "/", "\\") for c in config_path):
        return None
    
    return config_path
