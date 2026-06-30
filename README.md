# Navien NaviLink Water Heater — Home Assistant Integration

Control and monitor Navien water heaters connected to the Navien cloud via a
[NaviLink or NaviLink Lite](https://www.navieninc.com/accessories/navilink)
control system.

> **About this fork.** This is a stability-focused maintenance fork of the
> original integration by [nikshriv](https://github.com/nikshriv/hass_navien_water_heater)
> and the later fork by [bakerkj](https://github.com/bakerkj/hass_navien_water_heater),
> both of which appear unmaintained. The cloud protocol logic is unchanged from
> the original; **v2.0.0 rewrites the reconnect/lifecycle handling to fix a
> file-descriptor leak that could crash Home Assistant Core.** See
> [`CHANGELOG.md`](CHANGELOG.md) for the full list of fixes.

---

## What v2.0.0 fixes

If your Home Assistant log shows a slow build-up of these during a Navien cloud
outage, ending in Core restarting with exit code 1, this release is for you:

```
ERROR ... [custom_components.navien_water_heater.navien_api] Connection error during start up:
...
ERROR ... [homeassistant] Fatal error '[Errno 24] No file descriptors available' raised in event loop, shutting it down
```

Root cause was a leaked AWS IoT MQTT client (and its sockets) on every
reconnect, plus overlapping reconnect loops with no backoff. Details in the
changelog.

---

## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. In HACS, open the three-dot menu → **Custom repositories**.
3. Add this repository:
   - **URL:** `https://github.com/willh6/hass_navien_water_heater`
   - **Category:** Integration
4. Install **Navien NaviLink Water Heater**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & Services → Add Integration** and search for
   **Navien**.

### Manual

1. Copy the `custom_components/navien_water_heater` directory from this
   repository into your Home Assistant `config/custom_components/` directory.
   The result should be `config/custom_components/navien_water_heater/`.
2. Restart Home Assistant.
3. Add the integration via **Settings → Devices & Services**.

> **Upgrading from the nikshriv/bakerkj version?** This fork keeps the same
> `navien_water_heater` domain, so it is a drop-in replacement. Remove the old
> copy from `custom_components/`, add this one, and restart — your existing
> config entry and entities are preserved.

---

## Configuration

Setup is entirely through the UI. You'll be asked for:

- **Username / Password** — your NaviLink account credentials (the same ones
  you use in the NaviLink mobile app).
- **Device** — which NaviLink gateway to set up, if you have more than one.
- **Polling interval** — how often to poll the cloud, in seconds (min 10,
  max 120; default 15).

---

## Preheat / Recirculation "Hot Button" functionality

For water heaters with hot water recirculation (e.g. A or A2) via a dedicated
External Loop or [NaviCirc](https://www.navieninc.com/accessories/navicirc), you
can also directly control
[Hot Button](https://www.navieninc.com/accessories/hotbutton) functionality if a
Hot Button PCB is installed. This PCB is pre-installed on A2 models but must be
[installed](https://www.navieninc.com/downloads/hotbutton-installation-instructions-en)
as an add-on kit on older A models. The physical buttons do **not** need to be
connected to gain Hot Button functionality through this integration. Check the
NaviLink app to ensure everything is configured properly (Hot Button instead of
Schedule options). If you install this integration without Hot Button
functionality and later enable it, just reload the integration to add the
recirculation switch entity.

The preheat/recirculation parameters are inconsistently named between A and A2
models, and can be misleading (e.g. "interval time" is actually duration, while
"sample time" is the interval). This table helps decode them. Better
descriptions for A models can be found under Step 7.5.1.2 (pg 99) and Category 4
of Step 7.5.1.3 (pg 102) of the
[A2 installation manual](https://www.navieninc.com/downloads/npe-2-installation-and-operation-manual-en):

| A (see note 1)                      | A2                    | Description                                     | Notes                                     |
| ----------------------------------- | --------------------- | ----------------------------------------------- | ----------------------------------------- |
| Preheat Pump Output Time (P.12)     | Recirc Interval Time  | Recirculation Duration                          | See note 2. Hot Button 5 mins             |
| Preheat Interval Time (P.14)        | Recirc Sample Time    | Recirculation Interval                          | Hot Button N/A (not mentioned in manuals) |
| Preheat Off Offset Temp (P.15)      | Recirc Off Diff. Temp | Recirculation Off Delta                         | See note 2. Hot Button ---                |
| On-demand Pipe Target Length (P.16) | Fixture Distance      | Recirculation Off without External Temp Sensor  | See note 3                                |

1. For the A model, set per Step 6.5 (pgs 65-68) of the
   [A installation manual](https://www.navieninc.com/downloads/npe-a-s-manuals-installation-manual-en).
2. There are DIP switches on the Hot Button PCB (pg 34 of the A2 manual). Some
   users find they must set DIP switch 2 to ON for recirculation to heat to the
   setpoint. This changes the behavior of both settings as described on pg 102
   of the A2 manual.
3. If recirculation does not stay on long enough after Hot Button activation,
   try increasing to a much higher pipe length.

---

## Sample dashboard card

An example card to monitor and control a water heater including recirculation.
It uses these custom cards:
[ApexCharts](https://github.com/RomRider/apexcharts-card),
[Mushroom](https://github.com/piitaya/lovelace-mushroom),
[Card Mod](https://github.com/thomasloven/lovelace-card-mod), and
[Stack In Card](https://github.com/custom-cards/stack-in-card).

```yaml
- type: custom:stack-in-card
  mode: vertical
  cards:
    - type: custom:stack-in-card
      mode: horizontal
      cards:
        - type: tile
          entity: water_heater.house
          features:
            - type: target-temperature
          tap_action:
            action: toggle
          icon_tap_action:
            action: toggle
        - type: custom:mushroom-entity-card
          entity: switch.water_heater_recirculation
          icon_color: lime
          name: Recirculation
          layout: vertical
          card_mod:
            style: |
              mushroom-shape-icon {
                {% if states('switch.water_heater_recirculation') == 'on' %}
                  --shape-animation: spin 1.5s linear infinite;
                {% endif %}
              }
          tap_action:
            action: call-service
            service: switch.turn_on
            target:
              entity_id: switch.water_heater_recirculation
          icon_tap_action:
            action: call-service
            service: switch.turn_on
            target:
              entity_id: switch.water_heater_recirculation
        - type: custom:stack-in-card
          mode: vertical
          cards:
            - type: custom:apexcharts-card
              graph_span: 3h
              header:
                show: true
                title: Water Heater
              yaxis:
                - id: Temperature
                  opposite: true
                  decimals: 0
                  min: 70
                  max: 140
                  apex_config:
                    tickAmount: 7
                    title:
                      text: Temperature
                      style:
                        color: blue
                - id: Flow Rate
                  opposite: true
                  decimals: 0
                  min: 0
                  max: 4
                  apex_config:
                    tickAmount: 4
                    title:
                      text: Flow Rate
                      style:
                        color: green
              apex_config:
                labels:
                  useSeriesColors: true
                chart:
                  height: 300px
              series:
                - entity: switch.water_heater_power
                  name: Power
                  yaxis_id: Temperature
                  type: area
                  curve: stepline
                  extend_to: now
                  color: green
                  stroke_width: 0
                  opacity: 0.25
                  transform: "return x === 'on' ? 72 : 70;"
                  show:
                    in_header: false
                    legend_value: false
                - entity: sensor.water_heater_flow_rate
                  name: Flow Rate
                  yaxis_id: Flow Rate
                  color: green
                  stroke_width: 1
                  curve: stepline
                - entity: switch.water_heater_recirculation
                  name: Recirculation
                  yaxis_id: Temperature
                  type: area
                  curve: stepline
                  extend_to: now
                  color: lime
                  stroke_width: 0
                  opacity: 1.00
                  transform: "return x === 'on' ? 74 : 70;"
                  show:
                    in_header: false
                    legend_value: false
                - entity: sensor.water_heater_inlet_temperature
                  name: Inlet
                  yaxis_id: Temperature
                  color: lightblue
                  stroke_width: 2
                  curve: straight
                - entity: sensor.water_heater_outlet_temperature
                  name: Outlet
                  yaxis_id: Temperature
                  color: red
                  stroke_width: 2
                  curve: straight
```

---

## Sample automation

Run recirculation at the top and bottom of each hour from 5 AM to 10 PM:

```yaml
alias: Water Heater Recirculation
description: "Recirculation at the top and bottom of each hour from 5 AM to 10 PM."
trigger:
  - platform: time_pattern
    minutes: "0"
  - platform: time_pattern
    minutes: "30"
condition:
  - condition: time
    after: "04:55:00"
    before: "22:05:00"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.water_heater_recirculation
mode: single
```

---

## Credits

- Original integration: [nikshriv](https://github.com/nikshriv/hass_navien_water_heater)
- Subsequent fork: [bakerkj](https://github.com/bakerkj/hass_navien_water_heater)
- This stability fork: [willh6](https://github.com/willh6/hass_navien_water_heater)

Licensed under the [MIT License](LICENSE), with the original authors' copyright
retained.

> This is an unofficial integration and is not affiliated with or endorsed by
> Navien. It relies on Navien's cloud service, which may change without notice.
