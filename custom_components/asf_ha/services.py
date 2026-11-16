"""Services for ArchiSteamFarm integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_entry_oauth2_flow

from .const import (
    ATTR_BOT_NAME,
    ATTR_COMMAND,
    DOMAIN,
    SERVICE_EXECUTE_COMMAND,
    SERVICE_RESTART_BOT,
    SERVICE_START_BOT,
    SERVICE_STOP_BOT,
)

# ASF process control service names
SERVICE_START_ASF = "start_asf"
SERVICE_STOP_ASF = "stop_asf"
SERVICE_RESTART_ASF = "restart_asf"

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up services for ASF integration."""

    async def handle_restart_bot(call: ServiceCall) -> None:
        """Handle restart bot service."""
        bot_name = call.data.get(ATTR_BOT_NAME)
        _LOGGER.info(f"Restarting ASF bot: {bot_name}")
        
        # In a real implementation, this would call the ASF API
        # to restart the specified bot
        # For now, just log the action
        _LOGGER.debug(f"Would restart bot: {bot_name}")

    async def handle_stop_bot(call: ServiceCall) -> None:
        """Handle stop bot service."""
        bot_name = call.data.get(ATTR_BOT_NAME)
        _LOGGER.info(f"Stopping ASF bot: {bot_name}")
        
        # In a real implementation, this would call the ASF API
        # to stop the specified bot
        _LOGGER.debug(f"Would stop bot: {bot_name}")

    async def handle_start_bot(call: ServiceCall) -> None:
        """Handle start bot service."""
        bot_name = call.data.get(ATTR_BOT_NAME)
        _LOGGER.info(f"Starting ASF bot: {bot_name}")
        
        # In a real implementation, this would call the ASF API
        # to start the specified bot
        _LOGGER.debug(f"Would start bot: {bot_name}")

    async def handle_execute_command(call: ServiceCall) -> None:
        """Handle execute command service."""
        command = call.data.get(ATTR_COMMAND)
        _LOGGER.info(f"Executing ASF command: {command}")
        
        # In a real implementation, this would call the ASF API
        # to execute the specified command
        _LOGGER.debug(f"Would execute command: {command}")

    async def handle_start_asf(call: ServiceCall) -> None:
        """Handle start ASF service."""
        _LOGGER.info("Starting ASF process via service")
        
        # Get process manager from hass.data
        process_manager = None
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            process_manager = data.get("process_manager")
            if process_manager:
                break
        
        if process_manager:
            await process_manager.async_start()
        else:
            _LOGGER.error("No ASF process manager found")

    async def handle_stop_asf(call: ServiceCall) -> None:
        """Handle stop ASF service."""
        _LOGGER.info("Stopping ASF process via service")
        
        # Get process manager from hass.data
        process_manager = None
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            process_manager = data.get("process_manager")
            if process_manager:
                break
        
        if process_manager:
            await process_manager.async_stop()
        else:
            _LOGGER.error("No ASF process manager found")

    async def handle_restart_asf(call: ServiceCall) -> None:
        """Handle restart ASF service."""
        _LOGGER.info("Restarting ASF process via service")
        
        # Get process manager from hass.data
        process_manager = None
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            process_manager = data.get("process_manager")
            if process_manager:
                break
        
        if process_manager:
            await process_manager.async_restart()
        else:
            _LOGGER.error("No ASF process manager found")

    # Register services
    hass.services.async_register(DOMAIN, SERVICE_RESTART_BOT, handle_restart_bot)
    hass.services.async_register(DOMAIN, SERVICE_STOP_BOT, handle_stop_bot)
    hass.services.async_register(DOMAIN, SERVICE_START_BOT, handle_start_bot)
    hass.services.async_register(DOMAIN, SERVICE_EXECUTE_COMMAND, handle_execute_command)
    
    # Register ASF process control services
    hass.services.async_register(DOMAIN, SERVICE_START_ASF, handle_start_asf)
    hass.services.async_register(DOMAIN, SERVICE_STOP_ASF, handle_stop_asf)
    hass.services.async_register(DOMAIN, SERVICE_RESTART_ASF, handle_restart_asf)
