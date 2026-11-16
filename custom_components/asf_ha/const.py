"""Constants for ArchiSteamFarm integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "asf_ha"
DEFAULT_NAME = "ArchiSteamFarm"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# Configuration keys
CONF_ASF_HOST = "asf_host"
CONF_ASF_PORT = "asf_port"
CONF_ASF_USERNAME = "asf_username"
CONF_ASF_PASSWORD = "asf_password"
CONF_ASF_WEB_PORT = "asf_web_port"
CONF_ASF_CONFIG_PATH = "asf_config_path"

# Default values
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 1242
DEFAULT_WEB_PORT = 1242
DEFAULT_CONFIG_PATH = "asf"

# ASF API endpoints
ASF_API_BASE = "http://{host}:{port}/Api/ASF"
ASF_API_COMMAND = "{base}/Command"
ASF_API_BOTS = "{base}/Bots"
ASF_API_VERSION = "{base}/Version"

# Service names
SERVICE_RESTART_BOT = "restart_bot"
SERVICE_STOP_BOT = "stop_bot"
SERVICE_START_BOT = "start_bot"
SERVICE_EXECUTE_COMMAND = "execute_command"

# Attribute names
ATTR_BOT_NAME = "bot_name"
ATTR_COMMAND = "command"
ATTR_BOTS = "bots"
ATTR_STATUS = "status"
ATTR_VERSION = "version"

# Sensor types
SENSOR_BOTS_ONLINE = "bots_online"
SENSOR_BOTS_TOTAL = "bots_total"
SENSOR_VERSION = "asf_version"
SENSOR_STATUS = "asf_status"
