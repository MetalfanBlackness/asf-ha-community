"""Sensor platform for ArchiSteamFarm integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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

if TYPE_CHECKING:
    from . import ASFDataUpdateCoordinator


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
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=SENSOR_STATUS,
        name="ASF Status",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ASF sensor platform."""
    # Get the shared coordinator from hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
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
            name="ArchiSteamFarm Monitor (Community)",
            manufacturer="Community",
            model="ASF Monitor",
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
