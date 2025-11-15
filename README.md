# Virtual Motion Sensor (Home Assistant)

A simple custom integration that exposes a virtual motion `binary_sensor` which turns on when a specific Home Assistant event is fired and turns off automatically after a short duration. Useful for bridging arbitrary events (RF remotes, scripts, webhooks) into motion automations.

## How it works
- Listens on the HA event bus for a configured `event_type`.
- When an event arrives with `data.code` equal to your configured `event_code`, the sensor turns on.
- Subsequent events are debounced for a short period to avoid rapid re-triggers.
- The sensor automatically resets to off after a configurable number of seconds.
- An options flow lets you adjust timings after setup.

Entity details:
- `platform`: `binary_sensor`
- `device_class`: `motion`
- `should_poll`: `false` (push via events)
- Attributes: `last_triggered`, `reset_time`, `debounce_time`

## Installation
1. Copy this folder to `config/custom_components/virtual_motion_sensor` in your Home Assistant setup.
2. Restart Home Assistant.
3. Add the integration via Settings → Devices & Services → Add Integration → “Virtual Motion Sensor”.

## Configuration (UI)
You will be asked for:
- Name
- Event Type (string) — default: `esphome.rf_code_received`
- Event Code (matched against `event.data.code`)
- Reset Time (seconds)
- Debounce Time (seconds)

Defaults:
- Reset Time: 2s
- Debounce Time: 2s
 - Event Type: `esphome.rf_code_received`

After setup, go to the integration’s Options to adjust the timings at any time.

## Example: fire an event to trigger motion
Use the Developer Tools → Services and call:

```yaml
service: event.fire
data:
  event_type: my_motion_event
  event_data:
    code: hallway
```

If your sensor was configured with `event_type = my_motion_event` and `event_code = hallway`, it will turn on immediately and then turn off automatically after the reset duration.

## Example automation: transform any event into motion
```yaml
alias: "Map button press to virtual motion"
mode: single
trigger:
  - platform: event
    event_type: zigbee_event
    event_data:
      device_ieee: "00:11:22:33:44:55:66:77"
      command: "single"
action:
  - service: event.fire
    data:
      event_type: my_motion_event
      event_data:
        code: hallway
```

## Notes and limitations
- The event must include `event.data.code` equal to your configured `event_code`.
- Debounce prevents rapid re-triggering; a new trigger during debounce is ignored.
- Reset schedules a turn-off; a later valid trigger will reschedule the reset.

## License
MIT


