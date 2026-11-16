# ⚠️ ArchiSteamFarm Monitor (Community) - Unofficial Home Assistant Integration

**⚠️ IMPORTANT - Third-Party Integration**

**This is NOT an official ArchiSteamFarm integration.**

- ❌ NOT developed by JustArchi (ASF author)
- ❌ NOT officially supported by ArchiSteamFarm
- ✅ Community developed and maintained
- ✅ Use at your own risk

**Official ArchiSteamFarm:** https://github.com/JustArchi/ArchiSteamFarm
**This Integration:** Report issues to this repository only

---

## About

A **community-developed** Home Assistant custom integration for monitoring [ArchiSteamFarm (ASF)](https://github.com/JustArchi/ArchiSteamFarm).

> **Disclaimer**: This integration is a third-party, unofficial project. It is not affiliated with, endorsed by, or supported by JustArchi or the ArchiSteamFarm project. ArchiSteamFarm® is a trademark of its respective owners.

## Features

- Monitor ASF bot status (running/stopped)
- View bot statistics and game counts
- Start, stop, and restart individual bots
- Execute ASF commands
- View ASF version information
- Monitor total bots and online bots count

## Installation

### Method 1: Using HACS (Recommended)

1. Open HACS in your Home Assistant
2. Go to "Integrations" tab
3. Click "Explore & Download Repositories"
4. Search for "ArchiSteamFarm" or add this repository manually
5. Click "Download" and restart Home Assistant

### Method 2: Manual Installation

1. Copy the `custom_components/asf_ha` directory to your Home Assistant configuration directory
2. Restart Home Assistant
3. Go to Configuration > Integrations and add "ArchiSteamFarm"

## Configuration

### Configuration File Location

The integration automatically creates and manages ASF configuration files in a subdirectory of your Home Assistant configuration folder:

```
/config/
└── asf/                          # Default config subdirectory
    ├── ASF.json                  # Main ASF configuration
    ├── ASF.db                    # ASF database
    ├── logs/                     # ASF logs
    └── plugins/                  # ASF plugins
```

You can change the `asf` subdirectory to any name or path (e.g., `asf/config`) in the integration settings.

### Setting up ASF

Before using this integration, you need to have ArchiSteamFarm running and accessible from your Home Assistant server.

#### Option 1: Docker (Recommended)

```yaml
version: '3.8'
services:
  archisteamfarm:
    image: justarchi/archisteamfarm:latest
    container_name: archisteamfarm
    restart: unless-stopped
    volumes:
      - /path/to/asf/config:/app/config
      - /path/to/asf/logs:/app/logs
    ports:
      - "1242:1242"
    environment:
      - ASF_CULTURE=EN
```

#### Option 2: Direct Installation

1. Download ASF from [GitHub Releases](https://github.com/JustArchi/ArchiSteamFarm/releases)
2. Extract and configure `ASF.json`
3. Run ASF with IPC enabled: `ASF --ipc true --ipc-port 1242`

### Integration Setup

1. In Home Assistant, go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **ArchiSteamFarm**
4. Enter the connection details:
   - **Host**: IP or hostname where ASF is running (e.g., `192.168.1.100` or `localhost`)
   - **Port**: ASF IPC port (default: `1242`)
   - **Web Port**: ASF web interface port (default: `1242`)
   - **Config Subdirectory**: Subdirectory in Home Assistant config folder for ASF config files (default: `asf`)
5. Click **Submit**

## Entities

### Sensors

- **sensor.asf_bots_online**: Number of currently running bots
- **sensor.asf_bots_total**: Total number of configured bots
- **sensor.asf_version**: Current ASF version
- **sensor.asf_status**: Current ASF status

### Switches

- **switch.asf_bot_[botname]**: Turn bot on/off

### Buttons

- **button.asf_restart_[botname]**: Restart specific bot

## Services

The integration provides the following services:

### `asf_ha.restart_bot`

Restart a specific ASF bot.

**Fields:**
- `bot_name` (required): Name of the bot to restart

**Example:**
```yaml
action:
  service: asf_ha.restart_bot
  data:
    bot_name: "Bot1"
```

### `asf_ha.stop_bot`

Stop a specific ASF bot.

**Fields:**
- `bot_name` (required): Name of the bot to stop

**Example:**
```yaml
action:
  service: asf_ha.stop_bot
  data:
    bot_name: "Bot1"
```

### `asf_ha.start_bot`

Start a specific ASF bot.

**Fields:**
- `bot_name` (required): Name of the bot to start

**Example:**
```yaml
action:
  service: asf_ha.start_bot
  data:
    bot_name: "Bot1"
```

### `asf_ha.execute_command`

Execute a custom ASF command.

**Fields:**
- `command` (required): ASF command to execute

**Example:**
```yaml
action:
  service: asf_ha.execute_command
  data:
    command: "stats"
```

## Automation Examples

### Start all bots on Home Assistant startup

```yaml
alias: "Start ASF bots on HA startup"
trigger:
  - platform: homeassistant
    event: start
action:
  - service: asf_ha.start_bot
    data:
      bot_name: "Bot1"
  - service: asf_ha.start_bot
    data:
      bot_name: "Bot2"
```

### Restart bot when it goes offline

```yaml
alias: "Restart ASF bot when offline"
trigger:
  - platform: state
    entity_id: switch.asf_bot_bot1
    to: "off"
    for:
      hours: 1
      minutes: 0
      seconds: 0
action:
  - service: asf_ha.restart_bot
    data:
      bot_name: "Bot1"
```

## ASF Configuration

Make sure your `ASF.json` has IPC enabled:

```json
{
  "IPC": {
    "Enabled": true,
    "Host": "0.0.0.0",
    "Port": 1242,
    "Password": ""
  }
}
```

## Troubleshooting

### Connection Issues

- Verify ASF is running and accessible from your Home Assistant server
- Check that the port is open in your firewall
- Verify IPC is enabled in ASF configuration
- Try connecting to ASF web interface at `http://[host]:[port]`

### Integration Not Loading

- Restart Home Assistant after installation
- Check Home Assistant logs for errors
- Verify the `custom_components/asf_ha` directory is in your config directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This integration is provided as-is. ArchiSteamFarm is licensed under the [Apache License 2.0](https://github.com/JustArchi/ArchiSteamFarm/blob/master/LICENSE).

## Support

For issues with this integration, please open an issue on the repository.

For issues with ArchiSteamFarm itself, please refer to the [ASF GitHub repository](https://github.com/JustArchi/ArchiSteamFarm).
