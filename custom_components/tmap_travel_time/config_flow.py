from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

class TmapTravelTimeConfigFlow(config_entries.ConfigFlow, domain="tmap_travel_time"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        states = self.hass.states.async_all(["zone","device_tracker"])

        entity_ids = {}
        for state in states:
            entity_ids[state.entity_id] = f"{state.name}({state.entity_id})"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("start_entity"): vol.In(entity_ids),
                vol.Required("end_entity"): vol.In(entity_ids),
                vol.Required("api_key"): str,
                vol.Optional("scan_interval", default=900): int
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TmapTravelTimeOptionsFlow(config_entry)

class TmapTravelTimeOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Update config entry and reload
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("start_entity", default=self.config_entry.data.get("start_entity")): str,
                vol.Required("end_entity", default=self.config_entry.data.get("end_entity")): str,
                vol.Required("api_key", default=self.config_entry.data.get("api_key")): str,
                vol.Required("scan_interval", default=self.config_entry.data.get("scan_interval", 900)): int
            }),
            errors=errors,
        )
