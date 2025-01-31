"""Tmap Travel Time Integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .config_flow import TmapTravelTimeConfigFlow  # noqa: F401
from .sensor import async_setup_entry

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tmap_travel_time"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
  
