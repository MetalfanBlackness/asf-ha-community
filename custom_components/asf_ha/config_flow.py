"""Config flow for ArchiSteamFarm integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WEB_PORT,
    DEFAULT_CONFIG_PATH,
    DOMAIN,
    CONF_ASF_HOST,
    CONF_ASF_PORT,
    CONF_ASF_WEB_PORT,
    CONF_ASF_CONFIG_PATH,
)

_LOGGER = logging.getLogger(__name__)

# Schema for user input
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ASF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_ASF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_ASF_WEB_PORT, default=DEFAULT_WEB_PORT): int,
        vol.Optional(CONF_ASF_CONFIG_PATH, default=DEFAULT_CONFIG_PATH): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate that we can connect to ASF
    # For now, we'll just validate the input format
    host = data[CONF_ASF_HOST]
    port = data[CONF_ASF_PORT]
    
    # Basic validation
    if not host or not isinstance(host, str):
        raise InvalidHost
    
    if not (0 < port <= 65535):
        raise InvalidPort
    
    # Return info that you want to store in the config entry
    return {"title": f"ASF on {host}:{port}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ArchiSteamFarm."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["asf_host"] = "invalid_host"
            except InvalidPort:
                errors["asf_port"] = "invalid_port"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Handle import from YAML configuration."""
        return await self.async_step_user(import_config)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for ArchiSteamFarm."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ASF_HOST,
                        default=self.config_entry.data.get(CONF_ASF_HOST, DEFAULT_HOST),
                    ): str,
                    vol.Optional(
                        CONF_ASF_PORT,
                        default=self.config_entry.data.get(CONF_ASF_PORT, DEFAULT_PORT),
                    ): int,
                    vol.Optional(
                        CONF_ASF_WEB_PORT,
                        default=self.config_entry.data.get(CONF_ASF_WEB_PORT, DEFAULT_WEB_PORT),
                    ): int,
                    vol.Optional(
                        CONF_ASF_CONFIG_PATH,
                        default=self.config_entry.data.get(CONF_ASF_CONFIG_PATH, DEFAULT_CONFIG_PATH),
                    ): str,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


class InvalidPort(HomeAssistantError):
    """Error to indicate there is an invalid port."""
