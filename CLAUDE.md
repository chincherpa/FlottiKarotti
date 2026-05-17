# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Pygame version (current main version)
python pygame_app.py

# CLI version (older, German, uses rich library)
python main.py
```

No build step, no test suite. `test.py` is a scratch file for rich library experiments, not a test runner.

## Architecture

Two independent implementations of the same board game ("Flotti Karotti" — a children's rabbit racing game):

### `pygame_app.py` — Visual version (active development)

Four classes, cleanly separated:

| Class | Role |
|---|---|
| `Player` | Data only: position, image, color, active state |
| `GameState` | All game logic: deck, board dict, holes, movement, win detection |
| `Button` | Stateless UI component with hover |
| `FlottiKarottiGame` | Pygame loop, rendering, input routing |

**Board model:** `dBoard: dict[int, str]` mapping position 1–28 to `FREE / HOLE / TARGET / OCCUPIED`. Position 0 = off-board (start/waiting area).

**Movement rule:** `get_target_field()` skips positions occupied by other players — only `FREE`, `HOLE`, and `TARGET` cells count toward steps.

**Hole mechanic:** `HOLES_SEQUENCE = [13, 25, 16, 23, 4, 21, 7, 19, 10]` — each KLICK card advances to the next hole index (wraps). Previous hole is cleared. Any rabbit on the new hole position goes back to 0.

**Assets:** PNG files have timestamped names (e.g. `rabbit_blue_1768232001788.png`). `find_asset(prefix)` scans `assets/` by prefix — never hardcode the full filename.

**Debug mode:** `DEBUG = True` at top of file draws path lines and position indices on screen. Flip to `False` for clean rendering.

### `main.py` — CLI version (legacy)

Script-level code (no classes), uses `rich` for console output. German variable names (`dSpielerNamen`, `lHoles`, `dPlayers`). Same game constants as pygame version. Not intended for further development.

## Key Constants

```python
NUM_POSITIONS = 28
HOLES_SEQUENCE = [13, 25, 16, 23, 4, 21, 7, 19, 10]
CARDS = [1]*24 + [2]*8 + [3]*4 + ["KLICK"]*12  # 48 total
```

Players hardcoded to 2: Flora (blue rabbit) and Mathea (red rabbit).
