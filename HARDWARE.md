# Hardware Plan — Ava's Game Box

## Component Stack (top to bottom)
- HyperPixel 4.0 Square (720x720 touchscreen)
- Pimoroni LiPo SHIM (boosts 3.7V LiPo → 5.1V, sits on Pi header pins)
- Heatsink (copper/aluminum, in clearance gap between Pi SoC and SHIM)
- Raspberry Pi 5

## Power Architecture

```
LiPo Battery ── Y-connector JST ──┬── LiPo SHIM (boost to 5.1V → Pi header → powers everything)
                                   │
                                   └── Amigo Pro (USB-C charging only, not in power path to Pi)
```

- SHIM is the sole power source for the Pi + HyperPixel
- Amigo Pro only charges the battery via USB-C, outputs 4.2V max (not enough for Pi)
- Both share the battery through a Y-connector JST cable

## Switches

### Switch 1 — Soft On/Off (exposed, kid-friendly)
- **Type**: Momentary pushbutton (big, friendly, already have it)
- **Wired to**: J2 header pads on Pi 5
- **Function**: Clean soft shutdown / wake from halt
- **Behavior**: Press → Pi shuts down cleanly (SD card safe, screen goes dark). Press again → Pi boots, game auto-launches.
- **Mounting**: Front of enclosure, easy for Ava to reach

### Switch 2 — Hard Power Kill (hidden, parent-only)
- **Type**: SPST toggle switch (rated 3A+ for LiPo inrush current)
- **Wired to**: Inline on battery positive wire (breaks circuit completely)
- **Function**: Zero-drain power cut for storage/travel
- **Behavior**: Flip off → all power cut, zero battery drain. Flip on → power restored, press Switch 1 to boot.
- **Mounting**: Hidden compartment on back/bottom of enclosure, not accessible to toddler
- **IMPORTANT**: Only flip off AFTER soft shutdown has completed (activity LED stops)

### Usage Flow
1. **Daily use**: Press momentary button → game launches. Press again → clean shutdown.
2. **Storing/traveling**: After shutdown, flip toggle off → zero drain.
3. **Charging**: Plug USB-C into Amigo Pro (works regardless of toggle/Pi state).

## Thermal Management
- Pi 5 runs hot, especially sandwiched with SHIM + HyperPixel blocking airflow
- Low-profile copper or aluminum heatsink on Pi 5 SoC (fits in gap between Pi and SHIM)
- Enclosure must have ventilation — NOT foam (insulator), use 3D-printed case with vent holes
- Pi 5 thermal throttles at 85C, but aim to keep it under 70C
- Optional: 30-40mm 5V fan if passive cooling isn't enough

## Enclosure Requirements
- Fits: Pi 5 + SHIM + HyperPixel sandwich, Amigo Pro board, LiPo battery
- Front: HyperPixel screen flush/exposed, big momentary button accessible
- Back/bottom: Hidden compartment or recessed area for SPST toggle
- USB-C port: Accessible for Amigo Pro charging
- Ventilation: Vent holes or slots for heat dissipation (near Pi SoC area)
- No sharp edges (toddler-proof)

## Software Config (already done)
- Game auto-launches on boot via `~/.config/autostart/ava-game.desktop`
- J2 triggers instant shutdown via `HandlePowerKey=poweroff` in logind
- Shutdown script at `/lib/systemd/system-shutdown/screen-off.sh` kills backlight (TODO: install this, was interrupted)
- Touch sensitivity tuned: threshold=15, report_rate=20 via `hyperpixel-touch.service`

## TODO
- [ ] Install heatsink on Pi 5 SoC
- [ ] Install shutdown screen-off script (SSH in and run setup)
- [ ] Wire SPST toggle inline on battery positive
- [ ] Mount momentary button to enclosure front
- [ ] Design and print/build enclosure
- [ ] Check temps under load (`vcgencmd measure_temp`)
- [ ] Image SD card as backup
