"""Switch platform for ArchiSteamFarm integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    ATTR_BOTS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ASF switch platform."""
    # Get the coordinator from the sensor platform
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if coordinator is None:
        # Create a new coordinator if it doesn't exist
        from .sensor import ASFDataUpdateCoordinator
        coordinator = ASFDataUpdateCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Create switches for each bot
    entities: list[SwitchEntity] = []
    
    # Get bot data
    bot_data = coordinator.data.get("bots", [])
    
    for bot in bot_data:
        entities.append(
            ASFBotSwitch(coordinator, entry, bot["name"])
        )
    
    async_add_entities(entities)


class ASFBotSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an ASF bot switch."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        bot_name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._bot_name = bot_name
        self._attr_unique_id = f"{entry.entry_id}_bot_{bot_name}"
        self._attr_name = f"ASF Bot {bot_name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="ArchiSteamFarm",
            manufacturer="ArchiSteamFarm",
            model="Steam Bot",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    @property
    def is_on(self) -> bool:
        """Return true if the bot is running."""
        data = self.coordinator.data
        bots = data.get("bots", [])
        
        for bot in bots:
            if bot["name"] == self._bot_name:
                return bot["status"] == "Running"
        
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the bot on."""
        # In a real implementation, this would call the ASF API
        # to start the bot
        _LOGGER.info(f"Starting ASF bot: {self._bot_name}")
        
        # Update the coordinator data to reflect the change
        # This is a placeholder - in reality, you'd make an API call
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the bot off."""
        # In a real implementation, this would call the ASF API
        # to stop the bot
        _LOGGER.info(f"Stopping ASF bot: {self._bot_name}")
        
        # Update the coordinator data to reflect the change
        await self.coordinator.async_request_refresh()
