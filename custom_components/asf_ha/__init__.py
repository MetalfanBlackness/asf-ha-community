"""Custom integration for ArchiSteamFarm with Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_ASF_HOST,
    CONF_ASF_PORT,
    CONF_ASF_PASSWORD,
    ASF_API_BASE,
    ASF_API_COMMAND,
    ASF_API_BOTS,
    ASF_API_VERSION,
)
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
]


class ASFDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ASF data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get("scan_interval", 30)),
        )
        self._entry = entry
        self._asf_data: dict = {}
        self._host = entry.data.get(CONF_ASF_HOST, "localhost")
        self._port = entry.data.get(CONF_ASF_PORT, 1242)
        self._password = entry.data.get(CONF_ASF_PASSWORD, "")

    def _build_api_url(self, endpoint: str) -> str:
        """Build API URL with password if configured."""
        base_url = ASF_API_BASE.format(host=self._host, port=self._port)
        if self._password:
            return f"{base_url}{endpoint}?password={self._password}"
        return f"{base_url}{endpoint}"

    async def _async_update_data(self) -> dict:
        """Fetch data from ASF."""
        # TODO: Implement actual ASF API calls with password support
        try:
            # Build URLs with password if configured
            version_url = self._build_api_url(ASF_API_VERSION)
            bots_url = self._build_api_url(ASF_API_BOTS)
            
            _LOGGER.debug(f"Fetching ASF data from {self._host}:{self._port}")
            
            # Mock data - replace with actual API calls using aiohttp
            self._asf_data = {
                "bots_online": 0,
                "bots_total": 0,
                "version": "Unknown",
                "status": "Unknown",
                "bots": [],
            }
            return self._asf_data
        except Exception as e:
            _LOGGER.error(f"Error fetching ASF data: {e}")
            return self._asf_data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ArchiSteamFarm from a config entry."""
    _LOGGER.debug("Setting up ASF Monitor integration")
    
    # Initialize the ASF client
    hass.data.setdefault(DOMAIN, {})
    
    # Create and store the coordinator for all platforms to use
    coordinator = ASFDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
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
