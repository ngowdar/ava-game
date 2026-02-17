# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ava's Game Box — a Pygame-based touchscreen entertainment hub for a 3-year-old, designed for a 720x720 HyperPixel 4.0 Square display on a Raspberry Pi 5. Features games and Roku TV show launching.

## Running

```bash
python main.py
```

Requires `pygame` (`pip install pygame`). No other dependencies — Roku HTTP calls use `urllib` (stdlib).

## Architecture

Multi-file app using a state-machine pattern:

```
main.py              — Entry point: pygame init, game loop
app.py               — App class: state machine, screen routing, history stack
config.py            — Constants: colors, dimensions, show data, Roku IP
ui.py                — Shared UI: draw_button(), draw_back_button(), draw_card()
roku.py              — Roku HTTP helper (urllib, threaded fire-and-forget)
screens/
  main_menu.py       — "AVA" title + PLAY GAMES / WATCH SHOWS buttons
  games_menu.py      — 3 game cards grid
  bubble_pop.py      — Bubble-popping game (tap to pop + respawn)
  animal_sounds.py   — 3x3 animal tap grid with bounce/particle animations
  whack_a_critter.py — Whack-a-mole: 45s rounds, scoring, celebration
  shows.py           — 2-column paginated show cards, Roku deep-link launch
  remote.py          — D-pad + Home/Back/Play-Pause, Roku keypress
assets/
  shows/             — Show PNG images (280x120 after scaling)
```

### Navigation Flow

```
MAIN_MENU  ──►  GAMES_MENU  ──►  BUBBLE_POP
                             ──►  ANIMAL_SOUNDS
                             ──►  WHACK_A_CRITTER
           ──►  SHOWS       ──►  REMOTE
```

- `App` holds a dict of screen objects and a `history` stack
- `app.go_to(state)` pushes current state and switches; `app.go_back()` pops
- Every screen except MAIN_MENU shows a back button (top-left circle with `<` arrow)
- Each screen class implements: `on_enter()`, `handle_event(event)`, `update(dt)`, `draw(surface)`

## Key Constraints

- Resolution is locked to 720x720 for the HyperPixel 4.0 Square display
- Input must work via touchscreen (use MOUSEBUTTONDOWN, not keyboard events)
- Target audience is a toddler — keep interactions simple, colorful, and tap-based
- No audio hardware yet — sound hooks are commented out in config.py, ready to enable
- Roku IP is `10.0.0.60` (set in `config.py`)
- All Roku HTTP calls are threaded with 3s timeout to avoid UI freezes
- Uses `pygame.font.Font(None, size)` (default font) — not SysFont, which may not exist on Debian

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

## Adding a New Game

1. Create `screens/your_game.py` with a class implementing `on_enter()`, `handle_event(event)`, `update(dt)`, `draw(surface)`
2. Add a state constant to `config.py`
3. Register it in `main.py`: `app.register(YOUR_STATE, YourGameScreen(app))`
4. Add a card to `screens/games_menu.py` that navigates to it

## Enabling Sound

When audio hardware is connected:
1. Uncomment `ANIMAL_SOUNDS` dict in `config.py` and set correct `.wav` paths
2. Uncomment the sound playback block in `screens/animal_sounds.py` `_tap_animal()`
3. Add `pygame.mixer.init()` in `main.py` before the game loop
