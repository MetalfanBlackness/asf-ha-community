"""Custom integration for ArchiSteamFarm with Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .services import async_setup_services
from .utils import get_config_path, get_asf_config_file, get_logs_dir, get_plugins_dir

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ArchiSteamFarm from a config entry."""
    _LOGGER.debug("Setting up ASF integration")
    
    # Initialize the ASF client
    hass.data.setdefault(DOMAIN, {})
    
    # Get or create the config directory within Home Assistant's config
    config_path = get_config_path(hass, entry.data)
    _LOGGER.debug(f"Using ASF config directory: {config_path}")
    
    # Store config paths in hass.data for use by other components
    hass.data[DOMAIN][entry.entry_id] = {
        "config_path": config_path,
        "asf_config_file": get_asf_config_file(hass, entry.data),
        "logs_dir": get_logs_dir(hass, entry.data),
        "plugins_dir": get_plugins_dir(hass, entry.data),
    }
    
    # Set up services
    await async_setup_services(hass, entry)
    
    # Forward the setup to each platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
