"""Tmap Travel Time Integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    ServiceResponse,
    ServiceCall,
    SupportsResponse,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .config_flow import TmapTravelTimeConfigFlow  # noqa: F401
from .sensor import async_setup_entry

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tmap_travel_time"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    await _async_setup_service(hass, entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
    
async def _async_setup_service( hass: HomeAssistant, entry: ConfigEntry ) -> None:
    """서비스를 설정합니다."""

    session = async_get_clientsession(hass)

    async def _async_routes(call: ServiceCall) -> None:

        start_x = call.data.get("start_x", None)
        start_y = call.data.get("start_y", None)
        end_x = call.data.get("end_x", None)
        end_y = call.data.get("end_y", None)
        req_coord_type = call.data.get("req_coord_type", None)

        if not start_x or not start_y or not end_x or not end_y:
            _LOGGER.error(f"[{DOMAIN}] _async_routes API Error: {result.get('errorMessage', 'Unknown error')}")

        # API request configuration
        headers = {
            "appKey": entry.data["api_key"],
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "startX": start_x,
            "startY": start_y,
            "endX": end_x,
            "endY": end_y,
            "reqCoordType": req_coord_type,
            "version": 1
        }

        response = await session.post("https://apis.openapi.sk.com/tmap/routes", headers=headers, json=payload)
        
        result = await response.json()

        if response.status != 200:
            _LOGGER.error(f"[{DOMAIN}] _async_routes API Error: {result.get('errorMessage', 'Unknown error')}")

        total_time = result["features"][0]["properties"]["totalTime"]
        
        return result["features"][0]["properties"]

    hass.services.async_register(DOMAIN, "routes", _async_routes, supports_response=SupportsResponse.ONLY, )
