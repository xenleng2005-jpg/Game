# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
python tetris.py
```

Requires `pygame` (`pip install pygame`).

## Architecture

The entire game lives in `tetris.py` as three classes plus module-level constants:

- **`Board`** — Holds the 20×10 grid (`self.grid` as a list of lists of color indices). Responsible for collision detection (`is_valid`), locking pieces onto the grid (`lock`), and clearing completed lines.
- **`Piece`** — Represents the active tetromino. `cells(row, col, rot)` returns the list of absolute `(row, col)` positions for a given state, defaulting to the piece's current state.
- **`Game`** — Owns the pygame window, clock, and all game state. Orchestrates the game loop via `run()` → `handle_events()` / `update(dt)` / `draw()`.

### Key data structures

- `PIECES` — dict mapping piece name (`'I'`, `'O'`, …) to a list of 4 rotations, each rotation being a list of `(row, col)` offsets from the piece's anchor.
- `COLORS` — list indexed by color integer (0 = empty, 1–7 = piece colors), used in both `Board.draw` and `Piece.draw`.
- **7-bag randomizer**: `Game.bag` is refilled from `PIECE_NAMES` and shuffled each time it empties, ensuring every piece appears once per bag.

### Scoring and levelling

- `SCORE_TABLE` maps lines cleared (1–4) to base points; actual score = base × current level.
- Level increments every `LINES_PER_LEVEL` (10) lines.
- Drop interval: `max(800 - (level - 1) * 70, 80)` ms.

### Controls

| Key | Action |
|-----|--------|
| ← / → | Move left/right |
| ↑ | Rotate clockwise |
| Z | Rotate counter-clockwise |
| ↓ | Soft drop |
| Space | Hard drop |
| P | Pause/unpause |
| R | Restart (game over screen only) |
| Escape | Quit |
