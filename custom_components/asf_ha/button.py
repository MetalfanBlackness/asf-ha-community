"""Button platform for ArchiSteamFarm integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
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
    SERVICE_RESTART_BOT,
    ATTR_BOT_NAME,
)

_LOGGER = logging.getLogger(__name__)


BUTTON_TYPES: list[ButtonEntityDescription] = [
    ButtonEntityDescription(
        key="restart_bot",
        name="Restart Bot",
        icon="mdi:restart",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ASF button platform."""
    # Initialize hass.data[DOMAIN] if it doesn't exist
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if coordinator is None:
        # Create a new coordinator if it doesn't exist
        from .sensor import ASFDataUpdateCoordinator
        coordinator = ASFDataUpdateCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Create buttons for each bot
    entities: list[ButtonEntity] = []
    
    # Get bot data
    bot_data = coordinator.data.get("bots", [])
    
    for bot in bot_data:
        entities.append(
            ASFBotRestartButton(coordinator, entry, bot["name"])
        )
    
    async_add_entities(entities)


class ASFBotRestartButton(CoordinatorEntity, ButtonEntity):
    """Representation of an ASF bot restart button."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        bot_name: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._entry = entry
        self._bot_name = bot_name
        self._attr_unique_id = f"{entry.entry_id}_bot_{bot_name}_restart"
        self._attr_name = f"ASF Restart {bot_name}"

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info(f"Restarting ASF bot: {self._bot_name}")
        
        # Call the service to restart the bot
        await self.hass.services.async_call(
            DOMAIN,
            SERVICE_RESTART_BOT,
            {ATTR_BOT_NAME: self._bot_name},
        )
        
        # Update the coordinator data
        await self.coordinator.async_request_refresh()
