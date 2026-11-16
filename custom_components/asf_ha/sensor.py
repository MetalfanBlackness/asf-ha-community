"""Sensor platform for ArchiSteamFarm integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ATTR_BOTS,
    ATTR_STATUS,
    ATTR_VERSION,
    DOMAIN,
    SENSOR_BOTS_ONLINE,
    SENSOR_BOTS_TOTAL,
    SENSOR_STATUS,
    SENSOR_VERSION,
)

_LOGGER = logging.getLogger(__name__)


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
        self._asf_data: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from ASF."""
        # TODO: Implement actual ASF API calls
        # This is a placeholder that will be replaced with real API calls
        try:
            # In a real implementation, this would call the ASF API
            # For now, return mock data
            self._asf_data = {
                "bots_online": 2,
                "bots_total": 3,
                "version": "5.5.2.3",
                "status": "Running",
                "bots": [
                    {"name": "Bot1", "status": "Running", "games": 5},
                    {"name": "Bot2", "status": "Running", "games": 3},
                    {"name": "Bot3", "status": "Offline", "games": 0},
                ],
            }
            return self._asf_data
        except Exception as e:
            raise UpdateFailed(f"Error fetching ASF data: {e}") from e


SENSOR_TYPES: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key=SENSOR_BOTS_ONLINE,
        name="ASF Bots Online",
        native_unit_of_measurement="bots",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=SENSOR_BOTS_TOTAL,
        name="ASF Bots Total",
        native_unit_of_measurement="bots",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=SENSOR_VERSION,
        name="ASF Version",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=SENSOR_STATUS,
        name="ASF Status",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ASF sensor platform."""
    from .const import DOMAIN
    from .asf_process import ASFProcessManager
    
    # Initialize hass.data[DOMAIN] if it doesn't exist
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    # Get process manager
    process_manager = None
    if entry.entry_id in hass.data[DOMAIN]:
        process_manager = hass.data[DOMAIN][entry.entry_id].get("process_manager")
    
    # If process manager exists and ASF is not running, start it
    if process_manager and not process_manager.is_running():
        _LOGGER.info("ASF not running, attempting to start")
        await process_manager.async_start()
    
    coordinator = ASFDataUpdateCoordinator(hass, entry)
    
    # Start the coordinator
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as e:
        _LOGGER.error(f"Failed to refresh coordinator: {e}")
        # If coordinator fails, we might need to start ASF
        if process_manager and not process_manager.is_running():
            _LOGGER.info("Retrying ASF start after coordinator failure")
            await process_manager.async_start()
            try:
                await coordinator.async_config_entry_first_refresh()
            except Exception as e2:
                _LOGGER.error(f"Failed to refresh coordinator after retry: {e2}")
                return
    
    # Create sensors
    entities: list[SensorEntity] = []
    
    for description in SENSOR_TYPES:
        entities.append(
            ASFSensor(coordinator, entry, description)
        )
    
    async_add_entities(entities)


class ASFSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ASF sensor."""

    def __init__(
        self,
        coordinator: ASFDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="ArchiSteamFarm (Community)",
            manufacturer="Community",
            model="Unofficial ASF Integration",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        
        if self.entity_description.key == SENSOR_BOTS_ONLINE:
            return data.get("bots_online", 0)
        elif self.entity_description.key == SENSOR_BOTS_TOTAL:
            return data.get("bots_total", 0)
        elif self.entity_description.key == SENSOR_VERSION:
            return data.get("version", "Unknown")
        elif self.entity_description.key == SENSOR_STATUS:
            return data.get("status", "Unknown")
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        data = self.coordinator.data
        attrs = {
            "integration": "ArchiSteamFarm (Community)",
            "disclaimer": "Unofficial - Not supported by ASF developers",
            "official_site": "https://github.com/JustArchi/ArchiSteamFarm",
        }
        
        if self.entity_description.key in [SENSOR_BOTS_ONLINE, SENSOR_BOTS_TOTAL]:
            attrs[ATTR_BOTS] = data.get("bots", [])
        elif self.entity_description.key == SENSOR_STATUS:
            attrs[ATTR_STATUS] = data.get("status", "Unknown")
        elif self.entity_description.key == SENSOR_VERSION:
            attrs[ATTR_VERSION] = data.get("version", "Unknown")
        
        return attrs
