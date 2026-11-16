# ArchiSteamFarm Home Assistant Marketplace App - Setup Guide

## Project Structure

```
asf-ha/
├── manifest.json                    # Home Assistant marketplace manifest
├── docker-compose.yml               # Docker configuration for ASF
├── README.md                        # Main documentation
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
├── config/
│   └── ASF.json                     # ASF configuration template
└── custom_components/
    └── asf_ha/
        ├── __init__.py             # Main integration initialization
        ├── const.py                # Constants and configuration keys
        ├── config_flow.py          # Configuration flow handler
        ├── sensor.py               # Sensor platform implementation
        ├── switch.py               # Switch platform implementation
        ├── button.py               # Button platform implementation
        ├── services.py             # Custom services implementation
        ├── services.yaml           # Service definitions
        └── strings.json            # Localization strings
```

## Quick Start

### 1. Prepare Your ASF Instance

#### Option A: Using Docker (Recommended)

1. Create a directory for ASF configuration:
   ```bash
   mkdir -p /path/to/asf/config
   mkdir -p /path/to/asf/logs
   ```

2. Copy and customize the ASF configuration:
   ```bash
   cp asf-ha/config/ASF.json /path/to/asf/config/
   ```

3. Edit `ASF.json` with your Steam credentials and bot configurations.

4. Start ASF using Docker:
   ```bash
   docker-compose -f asf-ha/docker-compose.yml up -d
   ```

#### Option B: Direct Installation

1. Download ASF from [GitHub Releases](https://github.com/JustArchi/ArchiSteamFarm/releases)
2. Extract to a directory
3. Copy `ASF.json` from this project to the ASF directory
4. Edit `ASF.json` with your configuration
5. Run ASF:
   ```bash
   ./ArchiSteamFarm --ipc true --ipc-port 1242
   ```

### 2. Install the Home Assistant Integration

#### For Home Assistant Marketplace (HACS)

1. Package this project and submit it to HACS
2. Users can then install it through HACS > Integrations

#### For Manual Installation

1. Copy the `custom_components/asf_ha` directory to your Home Assistant configuration directory:
   ```bash
   cp -r asf-ha/custom_components/asf_ha /path/to/homeassistant/config/
   ```

2. Restart Home Assistant

3. Add the integration:
   - Go to **Settings** > **Devices & Services**
   - Click **Add Integration**
   - Search for **ArchiSteamFarm**
   - Enter your ASF connection details

### 3. Configure the Integration

When adding the integration, you'll need to provide:

- **ASF Host**: IP address or hostname where ASF is running
  - If ASF is on the same machine as Home Assistant: `localhost` or `127.0.0.1`
  - If ASF is on a different machine: the LAN IP address (e.g., `192.168.1.100`)

- **ASF IPC Port**: The port ASF is listening on for IPC commands (default: `1242`)

- **ASF Web Port**: The port for ASF web interface (default: `1242`)

- **Config Subdirectory**: Subdirectory in Home Assistant config folder for ASF configuration (default: `asf`)
  - This allows you to store ASF configuration files in a subdirectory like `/config/asf/` or `/config/asf/config/`
  - The integration will automatically create this directory if it doesn't exist

## Configuration Options

### ASF Configuration (ASF.json)

The provided `ASF.json` template includes the essential settings for IPC communication:

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

**Important:** Make sure IPC is enabled and the host is set to `0.0.0.0` to allow connections from other machines on your network.

### Home Assistant Configuration

After setup, you can configure additional options in the integration settings:

- **Scan Interval**: How frequently the integration should fetch data from ASF (default: 30 seconds)
- **Config Subdirectory**: Change the subdirectory where ASF configuration files are stored

### Configuration File Locations

The integration stores ASF configuration files in a subdirectory of your Home Assistant configuration folder:

```
/config/
└── asf/                          # Default config subdirectory
    ├── ASF.json                  # Main ASF configuration
    ├── ASF.db                    # ASF database
    ├── logs/                     # ASF logs directory
    │   └── ASF.log               # ASF log file
    └── plugins/                  # ASF plugins directory
```

You can change the `asf` subdirectory to any name you prefer, or use a nested path like `asf/config`.

## Testing the Integration

### Manual Testing

1. Ensure ASF is running and accessible
2. Add the integration in Home Assistant
3. Check that entities are created:
   - Sensors for bot counts, version, and status
   - Switches for each configured bot
   - Buttons for restarting bots

4. Test the services:
   - Use the Developer Tools > Services to call `asf_ha.restart_bot`
   - Create automations that use the services

### Running the Test Script

```bash
# Navigate to the project directory
cd asf-ha

# Run the test script
python scripts/test_integration.py
```

The test script will verify:
- All Python modules can be imported
- Constants are defined correctly
- manifest.json is valid

## Developing the Integration

### Prerequisites

- Python 3.10+
- Home Assistant development environment
- ASF instance for testing

### Development Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. For Home Assistant integration development, install:
   ```bash
   pip install homeassistant pytest pytest-homeassistant-custom-component
   ```

### Making Changes

1. Edit the files in `custom_components/asf_ha/`
2. Test changes with the test script
3. Test in a real Home Assistant instance

### Next Steps for Full Implementation

The current integration includes:
- ✅ Configuration flow
- ✅ Sensor platform (with mock data)
- ✅ Switch platform (with mock data)
- ✅ Button platform (with mock data)
- ✅ Service definitions

**To make it fully functional, you need to implement:**

1. **Actual ASF API Client** - Replace the mock data in `sensor.py` with real API calls to ASF IPC
2. **API Connection Handling** - Implement connection management in `__init__.py`
3. **Error Handling** - Add proper error handling for connection issues
4. **Authentication** - If ASF IPC has password protection, implement authentication
5. **Real Service Implementation** - Update `services.py` to make actual ASF API calls

### ASF IPC API Reference

ASF provides an IPC interface for programmatic control. Key endpoints:

- `POST /Api/ASF/Command` - Execute ASF commands
- `GET /Api/ASF/Bots` - Get bot list and status
- `GET /Api/ASF/Version` - Get ASF version
- `POST /Api/ASF/Bot/{botName}/Command` - Execute command on specific bot

Example commands:
- `stats` - Get bot statistics
- `start` - Start a bot
- `stop` - Stop a bot
- `restart` - Restart a bot

### Example API Implementation

Here's how you might implement the ASF API client:

```python
# In asf_ha/asf_client.py
import aiohttp
import async_timeout
from typing import Any, Optional

class ASFClient:
    def __init__(self, host: str, port: int, password: Optional[str] = None):
        self._host = host
        self._port = port
        self._password = password
        self._base_url = f"http://{host}:{port}/Api/ASF"
        self._session = None

    async def async_get_bots(self) -> list[dict[str, Any]]:
        """Get list of all bots."""
        url = f"{self._base_url}/Bots"
        async with async_timeout.timeout(10):
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ConnectionError(f"Failed to get bots: {response.status}")

    async def async_execute_command(self, command: str) -> dict[str, Any]:
        """Execute an ASF command."""
        url = f"{self._base_url}/Command"
        data = {"command": command}
        async with async_timeout.timeout(10):
            async with self._session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ConnectionError(f"Failed to execute command: {response.status}")
```

## Publishing to Home Assistant Marketplace

To publish this integration to the Home Assistant Marketplace (HACS):

1. **Prepare Your Repository**
   - Create a GitHub repository
   - Push your code
   - Create a release with version tags

2. **HACS Requirements**
   - Valid `manifest.json`
   - Proper directory structure
   - README with clear documentation
   - License file (recommended)

3. **Submit to HACS**
   - Visit [HACS Default Repositories](https://github.com/hacs/default)
   - Follow the contribution guidelines
   - Submit a pull request to add your integration

## Troubleshooting

### Common Issues

1. **Integration not appearing in Home Assistant**
   - Verify the `custom_components/asf_ha` directory is in your Home Assistant config directory
   - Check that all Python files have valid syntax
   - Restart Home Assistant completely
   - Check Home Assistant logs for errors

2. **Cannot connect to ASF**
   - Verify ASF is running
   - Check that IPC is enabled in ASF configuration
   - Verify the host and port are correct
   - Check that the port is accessible (no firewall blocking)
   - Test connection manually: `curl http://[host]:[port]/Api/ASF/Version`

3. **Entities not updating**
   - Check that the scan interval is not too long
   - Verify ASF is responding to API requests
   - Check Home Assistant logs for update errors

### Viewing Logs

In Home Assistant:
1. Go to **Settings** > **System** > **Logs**
2. Filter for `asf_ha` or `ArchiSteamFarm`

Or check the Home Assistant log file directly:
```bash
tail -f /path/to/homeassistant/config/home-assistant.log | grep asf_ha
```

## Security Considerations

1. **Network Security**
   - Run ASF on a secure network
   - Use firewall rules to restrict access to the IPC port
   - Consider using a reverse proxy with authentication

2. **Credentials**
   - Never commit `ASF.json` with real credentials to version control
   - Use environment variables or secrets for sensitive data
   - The `.gitignore` file already excludes `ASF.json`

3. **ASF Configuration**
   - Set strong passwords if using IPC authentication
   - Restrict access to the ASF web interface
   - Regularly update ASF to the latest version

## Additional Resources

- [ArchiSteamFarm GitHub](https://github.com/JustArchi/ArchiSteamFarm)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [ASF IPC Documentation](https://github.com/JustArchi/ArchiSteamFarm/wiki/IPC)

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Please ensure:
- Code follows PEP 8 style guidelines
- All existing tests pass
- New functionality is properly tested
- Documentation is updated
