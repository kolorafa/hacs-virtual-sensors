import logging
import asyncio
from datetime import datetime, timezone
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    _LOGGER.info("Setting up virtual motion sensor: %s", config.get("name"))
    sensor = VirtualMotionSensor(hass, config, config_entry.entry_id)
    async_add_entities([sensor], update_before_add=True)

class VirtualMotionSensor(BinarySensorEntity):
    def __init__(self, hass, config, entry_id):
        self._hass = hass
        self._name = config["name"]
        self._event_type = config["event_type"]
        self._event_code = config["event_code"]
        self._reset_time = config.get("reset_time", 2)
        self._debounce_time = config.get("debounce_time", 2)
        self._state = False
        self._last_triggered_monotonic = 0.0
        self._last_triggered_at = None
        self._entry_id = entry_id
        self._unsub_event = None
        self._reset_handle = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def should_poll(self):
        return False

    @property
    def unique_id(self):
        return self._entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": self._name,
            "manufacturer": "VirtualMotion",
            "model": "Emulated Sensor"
        }

    @property
    def device_class(self):
        return "motion"

    @property
    def extra_state_attributes(self):
        return {
            "last_triggered": self._last_triggered_at,
            "reset_time": self._reset_time,
            "debounce_time": self._debounce_time,
        }

    async def async_added_to_hass(self):
        # Subscribe to the event bus and keep unsubscribe handle
        self._unsub_event = self._hass.bus.async_listen(self._event_type, self._handle_event)

    async def async_will_remove_from_hass(self):
        # Unsubscribe from event bus
        if self._unsub_event is not None:
            self._unsub_event()
            self._unsub_event = None
        # Cancel any pending reset callback
        if self._reset_handle is not None:
            self._reset_handle.cancel()
            self._reset_handle = None

    @callback
    def _handle_event(self, event):
        code = event.data.get("code")
        now_monotonic = self._hass.loop.time()
        if code == self._event_code and now_monotonic - self._last_triggered_monotonic > self._debounce_time:
            self._last_triggered_monotonic = now_monotonic
            self._last_triggered_at = datetime.now(timezone.utc).isoformat()
            self._state = True
            self.async_write_ha_state()
            # Cancel previous reset timer if any, then schedule a new one
            if self._reset_handle is not None:
                self._reset_handle.cancel()
            self._reset_handle = self._hass.loop.call_later(self._reset_time, self._reset_state)

    @callback
    def _reset_state(self):
        self._state = False
        self.async_write_ha_state()

