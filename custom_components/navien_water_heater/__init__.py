"""The Navien NaviLink Water Heater Integration.

Stability fork maintained by willh6. Original work by nikshriv and bakerkj.
"""
from __future__ import annotations

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION
from .navien_api import NavilinkConnect

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["water_heater", "sensor", "switch"]

CERT_SUBDIRS = ("custom_components", "navien_water_heater", "cert")
CERT_FILENAME = "AmazonRootCA1.pem"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Navien NaviLink Water Heater Integration from a config entry."""
    _LOGGER.debug("Setting up navien_water_heater (version %s)", VERSION)
    hass.data.setdefault(DOMAIN, {})

    aws_cert_path = os.path.join(hass.config.path(), *CERT_SUBDIRS, CERT_FILENAME)

    navilink = NavilinkConnect(
        userId=entry.data.get("username", ""),
        passwd=entry.data.get("password", ""),
        polling_interval=entry.data.get("polling_interval", 15),
        device_index=entry.data.get("device_index", 0),
        aws_cert_path=aws_cert_path,
    )
    hass.data[DOMAIN][entry.entry_id] = navilink

    await navilink.start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry, releasing the NaviLink connection cleanly."""
    navilink = hass.data[DOMAIN].get(entry.entry_id)
    if navilink is not None:
        # Ensure the cloud connection and its sockets are released before the
        # platforms are torn down, so reloads can't accumulate stale clients.
        await navilink.disconnect()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
