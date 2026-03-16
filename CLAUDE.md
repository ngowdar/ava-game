# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ava's Game Box — a Pygame-based touchscreen entertainment hub for a 3-year-old, designed for a 720x720 HyperPixel 4.0 Square display on a Raspberry Pi 5. Features games, Roku TV show launching, and YouTube video playback via Roku.

## Running

```bash
python main.py
```

Requires `pygame` (`pip install pygame`). No other dependencies — Roku HTTP calls use `urllib` (stdlib).

## Architecture

Multi-file app using a state-machine pattern:

```
main.py              — Entry point: pygame init, game loop
app.py               — App class: state machine, screen routing, status overlays
config.py            — Constants: colors, dimensions, show/video data, Roku IP, admin PIN
ui.py                — Shared UI: buttons, cards, fonts (IBM Plex Sans/Serif), status indicators
roku.py              — Roku HTTP helper (urllib, threaded fire-and-forget)
battery.py           — Battery level + WiFi status readers (pluggable backends)
screens/
  main_menu.py       — "AVA" title + PLAY GAMES / WATCH SHOWS / COOL VIDEOS + hidden shutdown
  games_menu.py      — 2x3 game cards grid
  finger_paint.py    — Free-draw canvas with palette, brushes, stamps
  shape_sorter.py    — Drag 5 shapes to matching cutouts
  magic_garden.py    — Tap to plant flowers, trees, butterflies, bees
  fireworks.py       — Tap to launch rockets that explode into particles
  particle_playground.py — Performance showcase: 2500 particles, 4 modes
  weather_toy.py     — 5 weather scenes (snow, rain, fireflies, blossoms, aurora)
  shows.py           — 2-column paginated show cards, Roku deep-link launch
  remote.py          — D-pad + Home/Back/Play-Pause, Roku keypress
  videos.py          — YouTube video cards with thumbnails, launches via Roku
assets/
  fonts/             — IBM Plex Sans + Serif (Bold & Regular .ttf)
  shows/             — Show PNG images (280x120 after scaling)
  videos/            — YouTube video thumbnail JPGs (scaled to card size)
```

### Navigation Flow

```
MAIN_MENU  ──►  GAMES_MENU  ──►  FINGER_PAINT
                             ──►  SHAPE_SORTER
                             ──►  MAGIC_GARDEN
                             ──►  FIREWORKS
                             ──►  PARTICLE_PLAYGROUND
                             ──►  WEATHER_TOY
           ──►  SHOWS       ──►  REMOTE
           ──►  VIDEOS
```

- `App` holds a dict of screen objects and a `history` stack
- `app.go_to(state)` pushes current state and switches; `app.go_back()` pops
- Every screen except MAIN_MENU shows a back button (top-left circle with `<` arrow)
- Each screen class implements: `on_enter()`, `handle_event(event)`, `update(dt)`, `draw(surface)`

### Status Indicators

Drawn on every screen by `app.py`:
- **Battery** (bottom-right): green >50%, yellow 20-50%, red <20%, "?" if no hardware
- **WiFi** (bottom-left): green connected, red disconnected

Battery reads from MAX17048 I2C → `/tmp/battery_pct` file → LiPo SHIM GPIO → None.
WiFi reads `/sys/class/net/wlan0/operstate`. Both cached, polled every 30 seconds.

### Admin Shutdown

Hidden on the main menu — not visible to the child:
1. Tap the top-right corner (80x80 invisible zone) **5 times within 3 seconds**
2. A PIN keypad overlay appears — enter the 4-digit PIN (set in `config.py`)
3. Correct PIN exits to desktop or powers off the Pi (configurable via `SHUTDOWN_ACTION`)

## Key Constraints

- Resolution is locked to 720x720 for the HyperPixel 4.0 Square display
- Input must work via touchscreen (use MOUSEBUTTONDOWN, not keyboard events)
- Target audience is a toddler — keep interactions simple, colorful, and tap-based
- No audio hardware yet — sound hooks are commented out in config.py, ready to enable
- Roku IP is `10.0.0.60` (set in `config.py`)
- All Roku HTTP calls are threaded with 3s timeout to avoid UI freezes
- Fonts: IBM Plex Sans (default) and Serif bundled in `assets/fonts/`, with DejaVu Sans fallback

## Fonts

Uses IBM Plex Sans as the primary font, with Serif available:

```python
get_font(36)                          # Plex Sans Bold (default everywhere)
get_font(24, bold=False)              # Plex Sans Regular
get_font(36, family="serif")          # Plex Serif Bold
get_font(24, bold=False, family="serif")  # Plex Serif Regular
```

Falls back to DejaVu Sans (Pi OS default) → pygame default font if files are missing.

## Adding a New Show

1. Find the content ID:
   - **Disney+**: Go to disneyplus.com, navigate to the show. The URL contains a UUID after `entity-` or after the last `/`.
   - **Netflix**: Go to netflix.com/title/XXXXXXXX. Copy the number.
2. Add a tuple to `SHOWS_DATA` in `config.py`:
   ```python
   ("Show Name", channel_id, "content_id", "movie_or_series", (R, G, B), "image_file.png"),
   ```
3. Place a PNG image in `assets/shows/` (any size — it gets scaled to 280x120). If no image, set the last field to `None` and the card will show the name as text.

### Channel IDs

| Service  | Channel ID |
|----------|-----------|
| Disney+  | 291097    |
| Netflix  | 12        |
| Hulu     | 2285      |
| YouTube  | 837       |
| HBO Max  | 61322     |
| Peacock  | 593099    |

## Adding a New Video

1. Go to youtube.com, find the video, copy the ID from the URL
   (e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ` → ID is `dQw4w9WgXcQ`)
2. Save a thumbnail to `assets/videos/` (any size — gets scaled to fit card).
   Quick way: `https://img.youtube.com/vi/VIDEO_ID/mqdefault.jpg`
3. Add a tuple to `VIDEOS_DATA` in `config.py`:
   ```python
   ("Title", "VIDEO_ID", (R, G, B), "thumbnail.jpg"),
   ```
   Videos launch on the TV via the Roku YouTube app (channel 837).

## Adding a New Game

1. Create `screens/your_game.py` with a class implementing `on_enter()`, `handle_event(event)`, `update(dt)`, `draw(surface)`
2. Add a state constant to `config.py`
3. Register it in `main.py`: `app.register(YOUR_STATE, YourGameScreen(app))`
4. Add a card to `screens/games_menu.py` that navigates to it

## Enabling Sound

When audio hardware is connected:
1. Uncomment `SOUNDS` dict in `config.py` and set correct `.wav` paths
2. Add `pygame.mixer.init()` in `main.py` before the game loop

## Deployment

Pi is at `10.0.0.210`, user `gowdar`, SSH key auth configured:
```bash
scp *.py gowdar@10.0.0.210:~/ava-game/
scp screens/*.py gowdar@10.0.0.210:~/ava-game/screens/
scp assets/fonts/*.ttf gowdar@10.0.0.210:~/ava-game/assets/fonts/
scp assets/videos/*.jpg gowdar@10.0.0.210:~/ava-game/assets/videos/
```
