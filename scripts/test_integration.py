#!/usr/bin/env python3
"""Test script for ASF Home Assistant integration."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the custom component to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from asf_ha.const import DOMAIN

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger(__name__)


async def test_imports():
    """Test that all modules can be imported."""
    _LOGGER.info("Testing imports...")
    
    try:
        from asf_ha import __init__, const, config_flow, sensor, switch, button, services
        _LOGGER.success("All imports successful")
        return True
    except ImportError as e:
        _LOGGER.error(f"Import error: {e}")
        return False


async def test_constants():
    """Test that constants are defined correctly."""
    _LOGGER.info("Testing constants...")
    
    from asf_ha.const import (
        DOMAIN,
        CONF_ASF_HOST,
        CONF_ASF_PORT,
        CONF_ASF_WEB_PORT,
        SENSOR_BOTS_ONLINE,
        SENSOR_BOTS_TOTAL,
        SENSOR_VERSION,
        SENSOR_STATUS,
        SERVICE_RESTART_BOT,
        SERVICE_STOP_BOT,
        SERVICE_START_BOT,
        SERVICE_EXECUTE_COMMAND,
    )
    
    assert DOMAIN == "asf_ha", "Domain should be 'asf_ha'"
    assert CONF_ASF_HOST == "asf_host", "Host config key should be 'asf_host'"
    assert CONF_ASF_PORT == "asf_port", "Port config key should be 'asf_port'"
    
    _LOGGER.success("Constants test passed")
    return True


async def test_manifest():
    """Test that manifest.json is valid."""
    _LOGGER.info("Testing manifest.json...")
    
    import json
    from pathlib import Path
    
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    
    if not manifest_path.exists():
        _LOGGER.error(f"Manifest file not found: {manifest_path}")
        return False
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_keys = ["domain", "name", "version", "config_flow"]
        for key in required_keys:
            if key not in manifest:
                _LOGGER.error(f"Missing required key in manifest: {key}")
                return False
        
        if manifest["domain"] != DOMAIN:
            _LOGGER.error(f"Domain mismatch: manifest={manifest['domain']}, const={DOMAIN}")
            return False
        
        _LOGGER.success("Manifest test passed")
        return True
    except json.JSONDecodeError as e:
        _LOGGER.error(f"Invalid JSON in manifest: {e}")
        return False


async def main():
    """Run all tests."""
    _LOGGER.info("Starting ASF HA integration tests...")
    
    tests = [
        test_imports,
        test_constants,
        test_manifest,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            _LOGGER.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    _LOGGER.info(f"\nTest Results: {passed}/{total} passed")
    
    if passed == total:
        _LOGGER.success("All tests passed!")
        return 0
    else:
        _LOGGER.error("Some tests failed")
        return 1


if __name__ == "__main__":
    # Add a success method to logger for colored output
    logging.Logger.success = lambda self, msg: self.info(f"✓ {msg}")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
