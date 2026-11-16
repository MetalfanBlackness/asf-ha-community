"""ASF Process Manager - Manages ArchiSteamFarm subprocess."""

from __future__ import annotations

import asyncio
import logging
import signal
import subprocess
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_ASF_HOST,
    CONF_ASF_PORT,
    CONF_ASF_WEB_PORT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WEB_PORT,
)
from .utils import get_config_path, get_asf_config_file, get_logs_dir

_LOGGER = logging.getLogger(__name__)


class ASFProcessManager:
    """Manages the ASF subprocess lifecycle."""

    def __init__(self, hass: HomeAssistant, entry_data: dict[str, Any]) -> None:
        """Initialize the process manager."""
        self.hass = hass
        self.entry_data = entry_data
        self._process: subprocess.Popen | None = None
        self._config_path = get_config_path(hass, entry_data)
        self._config_file = get_asf_config_file(hass, entry_data)
        self._logs_dir = get_logs_dir(hass, entry_data)
        self._asf_executable = entry_data.get("asf_executable", "ASF")
        self._auto_start = entry_data.get("auto_start", True)

    async def async_start(self) -> bool:
        """Start the ASF process."""
        if self.is_running():
            _LOGGER.warning("ASF is already running")
            return True

        if not self._config_file.exists():
            _LOGGER.info("Creating default ASF configuration")
            self._create_default_config()

        _LOGGER.info(f"Starting ASF from {self._asf_executable}")

        # Build command
        host = self.entry_data.get(CONF_ASF_HOST, DEFAULT_HOST)
        port = self.entry_data.get(CONF_ASF_PORT, DEFAULT_PORT)
        web_port = self.entry_data.get(CONF_ASF_WEB_PORT, DEFAULT_WEB_PORT)

        cmd = [
            str(self._asf_executable),
            "--ipc", "true",
            "--ipc-port", str(port),
            "--config", str(self._config_file),
            "--logs", str(self._logs_dir),
        ]

        # Start process
        try:
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self._config_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _LOGGER.info(f"ASF started with PID: {self._process.pid}")
        except FileNotFoundError as e:
            _LOGGER.error(f"Failed to start ASF: executable not found at {self._asf_executable}: {e}")
            self._process = None
            return False
        except PermissionError as e:
            _LOGGER.error(f"Failed to start ASF: permission denied for {self._asf_executable}: {e}")
            self._process = None
            return False
        except Exception as e:
            _LOGGER.error(f"Failed to start ASF: {e}")
            self._process = None
            return False

        # Wait for ASF to be ready
        await self._wait_for_ready()

        return True

    async def async_stop(self) -> bool:
        """Stop the ASF process."""
        if not self.is_running():
            _LOGGER.warning("ASF is not running")
            return True

        _LOGGER.info(f"Stopping ASF (PID: {self._process.pid})")

        # Send SIGTERM
        try:
            self._process.terminate()
        except ProcessLookupError:
            _LOGGER.warning("ASF process not found")
            self._process = None
            return True

        # Wait for termination
        try:
            await asyncio.wait_for(
                self._wait_for_process(),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            _LOGGER.warning("ASF did not stop gracefully, killing")
            try:
                self._process.kill()
                await self._wait_for_process()
            except Exception:
                pass

        self._process = None
        _LOGGER.info("ASF stopped")

        return True

    async def async_restart(self) -> bool:
        """Restart the ASF process."""
        await self.async_stop()
        await asyncio.sleep(2)
        return await self.async_start()

    def is_running(self) -> bool:
        """Check if ASF process is running."""
        if self._process is None:
            return False
        return self._process.poll() is None

    async def _wait_for_process(self) -> None:
        """Wait for the process to finish."""
        if self._process:
            await self.hass.async_add_executor_job(self._process.wait)

    async def _wait_for_ready(self, timeout: int = 30) -> bool:
        """Wait for ASF to be ready to accept connections."""
        try:
            import aiohttp
            import async_timeout
        except ImportError:
            _LOGGER.error("aiohttp not available, cannot check ASF readiness")
            return True

        host = self.entry_data.get(CONF_ASF_HOST, DEFAULT_HOST)
        port = self.entry_data.get(CONF_ASF_PORT, DEFAULT_PORT)

        url = f"http://{host}:{port}/Api/ASF/Version"

        for attempt in range(timeout):
            try:
                async with async_timeout.timeout(1):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                _LOGGER.info("ASF is ready")
                                return True
            except Exception as e:
                _LOGGER.debug(f"ASF not ready yet (attempt {attempt + 1}/{timeout}): {e}")
                await asyncio.sleep(1)

        _LOGGER.error("ASF did not become ready within timeout")
        return False

    def _create_default_config(self) -> None:
        """Create a default ASF configuration file."""
        import json

        port = self.entry_data.get(CONF_ASF_PORT, DEFAULT_PORT)
        web_port = self.entry_data.get(CONF_ASF_WEB_PORT, DEFAULT_WEB_PORT)

        config = {
            "CurrentCulture": "en-US",
            "SteamOwnerID": None,
            "Bots": [],
            "IPC": {
                "Enabled": True,
                "Host": "0.0.0.0",
                "Port": port,
                "Password": ""
            },
            "Database": {
                "Provider": "SQLite",
                "ConnectionString": f"Data Source={self._config_path / 'ASF.db'}"
            },
            "Logging": {
                "Level": "Info",
                "Output": "File",
                "FilePath": f"logs/ASF.log",
                "MaxSize": 10,
                "MaxFiles": 5
            },
            "Web": {
                "Enabled": True,
                "Host": "0.0.0.0",
                "Port": web_port,
            },
            "CommandProcessor": {
                "Enabled": True,
                "Commands": []
            }
        }

        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        _LOGGER.info(f"Created default ASF config at {self._config_file}")
