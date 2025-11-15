import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class VirtualMotionSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("event_type", default="esphome.rf_code_received"): str,
                vol.Required("event_code"): str,
                vol.Optional("reset_time", default=2): int,
                vol.Optional("debounce_time", default=2): int,
            }),
        )


class VirtualMotionSensorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options or {}
        data = self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("reset_time", default=current.get("reset_time", data.get("reset_time", 2))): int,
                vol.Optional("debounce_time", default=current.get("debounce_time", data.get("debounce_time", 2))): int,
            }),
        )


async def async_get_options_flow(config_entry):
    return VirtualMotionSensorOptionsFlow(config_entry)

