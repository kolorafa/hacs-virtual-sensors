import logging
from .const import DOMAIN

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

async def _update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    # Merge options into data for easy access across the platform
    hass.data[DOMAIN][entry.entry_id] = {**entry.data, **entry.options}

    # 🔥 To uruchamia binary_sensor.py
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])

    # Reload entity when options change
    entry.async_on_unload(entry.add_update_listener(_update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
