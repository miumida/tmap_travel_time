from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.restore_state import RestoreEntity
import aiohttp
import async_timeout
import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor through config entry."""
    coordinator = TmapDataCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([TmapTravelTimeSensor(coordinator, config_entry)])

class TmapDataCoordinator(DataUpdateCoordinator):
    """Data update coordinator for TMAP API."""

    def __init__(self, hass, config_entry):
        super().__init__(
            hass,
            _LOGGER,
            name="TMAP Travel Time",
            update_interval=timedelta(
                seconds=config_entry.data.get("scan_interval", 900)
            ),
        )
        self.config_entry = config_entry

    async def _async_update_data(self):
        """Fetch data from TMAP API."""
        try:
            start_entity = self.config_entry.data["start_entity"]
            end_entity = self.config_entry.data["end_entity"]
            
            # Get coordinates from entities
            start_state = self.hass.states.get(start_entity)
            end_state = self.hass.states.get(end_entity)
            
            if not start_state or not end_state:
                raise UpdateFailed("Entity not found")
                
            start_lon = start_state.attributes.get("longitude")
            start_lat = start_state.attributes.get("latitude")
            end_lon = end_state.attributes.get("longitude")
            end_lat = end_state.attributes.get("latitude")

            if None in (start_lon, start_lat, end_lon, end_lat):
                raise UpdateFailed("Invalid coordinates")

            # API request configuration
            headers = {
                "appKey": self.config_entry.data["api_key"],
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            payload = {
                "startX": start_lon,
                "startY": start_lat,
                "endX": end_lon,
                "endY": end_lat,
                "reqCoordType": "WGS84GEO",
                "version": 1
            }

            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        "https://apis.openapi.sk.com/tmap/routes",
                        headers=headers,
                        json=payload
                    )
                    result = await response.json()

            if response.status != 200:
                raise UpdateFailed(f"API Error: {result.get('errorMessage', 'Unknown error')}")

            total_time = result["features"][0]["properties"]["totalTime"]
            return round(total_time / 60)

        except Exception as e:
            raise UpdateFailed(f"Error updating travel time: {str(e)}")

class TmapTravelTimeSensor(SensorEntity, RestoreEntity):
    """Representation of a TMAP Travel Time sensor."""

    def __init__(self, coordinator, config_entry):
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"tmap_travel_time_{config_entry.entry_id}"
        self._attr_name = config_entry.data["name"]
        self._attr_native_unit_of_measurement = "분"
        self._attr_icon = "mdi:timelapse"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data if self.coordinator.data else None

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )
      
