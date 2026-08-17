*This project has been created as part of the 42 curriculum by abenabde, ayhammou.*

---

# 🕹️Run-Man: Treasure Adventure

## Description

A Pac-Man inspired game developed in Python as part of the 42 school curriculum. The player navigates a procedurally generated maze, eating pacgums and super-pacgums while avoiding (or hunting!) ghosts. The game features 10 progressively larger levels, a real-time HUD, a pause menu, a highscore system, cheat codes for peer review, and a complete SDL2-based graphical interface with sounds and animations.

The project is structured around a clean separation between the game engine (logic) and the display/input layers, making the codebase modular and easy to maintain.

---

## Instructions

### Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- SDL2, SDL2_ttf, SDL2_mixer (system libraries)

### Installation & Run

```bash
make run
```

This command will automatically install all Python dependencies (via `uv sync`) and the bundled `mazegenerator` package, then launch the game with the default `config.json`.

### Manual run

```bash
uv run python src/pac-man.py config.json
```

### Other Makefile targets

| Command | Description |
|---|---|
| `make install` | Install dependencies only |
| `make debug` | Run with Python debugger (pdb) |
| `make lint` | Run flake8 + mypy checks |
| `make lint-strict` | Run mypy in strict mode |
| `make clean` | Remove `__pycache__` and mypy cache |
| `make fclean` | Full clean including virtualenv |

### Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move Run-Man |
| Escape | Pause / open pause menu |
| `/cheat` + Enter | Enable invincibility (ghosts can't kill Run-Man) and boost player speed by ×1.25 each time it's entered (repeatable, capped at max speed) |
| `/speed` + Enter | Instantly set player speed to a fixed fast value |
| `/slow` + Enter | Slightly decrease player speed (repeatable) |
| `/next` + Enter | Skip to next level |

---

## Configuration

The game is highly customizable via the `config.json` file.
Default
* **Robust Parsing**: Our parser safely handles comments starting with `#` (which standard JSON does not support) and automatically applies secure fallback values if keys are missing or invalid.
* **Dynamic Balancing**: Instead of static global timers, the engine calculates the time limit for each level dynamically based on the total grid size (`time = (width × height) / 1.4`).

The game reads its settings from a JSON file passed as a command-line argument (default: `config.json`). Lines starting with `#` are treated as comments and ignored.

### Available settings

| Key | Type | Default | Description |
|---|---|---|---|
| `highscore_filename` | string | `"highscores.json"` | Path to the highscore file |
| `lives` | int | `3` | Starting lives (1–99) |
| `points_per_pacgum` | int | `10` | Points for eating a pacgum (1–100000) |
| `points_per_super_pacgum` | int | `50` | Points for eating a super-pacgum (1–100000) |
| `points_per_ghost` | int | `200` | Points for eating an edible ghost (1–100000) |
| `seed` | int | `42` | Base seed for maze generation (only used for level 1, see below) |
| `level` | list | see below | Per-level width/height configuration |

### Level configuration

Each entry in the `level` list defines the maze dimensions for that level. Width and height are clamped to `[10, 65]`; invalid or out-of-range values are automatically replaced with a safe default.

```json
{
  "level": [
    {"width": 15, "height": 15},
    {"width": 25, "height": 25},
    ...
  ]
}
```

If the player reaches a level beyond the configured list, the last configured level is reused.

---

## Highscore

Scores are stored in a JSON file (default: `highscores.json`) as a list of `{"name": ..., "score": ...}` objects, sorted in descending order. Only the **top 10** scores are kept.

When a game ends (win or loss), the player is prompted to enter their name (alphanumeric only, max 10 characters). The score is then inserted, the list re-sorted, and the file saved.

On load, the file is validated: entries with non-alphanumeric names, negative scores, or wrong types are silently discarded. A missing or corrupt file is handled gracefully — a fresh list is started without crashing.

This approach was chosen for its simplicity and portability: no database is needed, the file is human-readable, and it can easily be shared or reset by the player.

---

## Maze Generation

Mazes are generated using the bundled **A-Maze-ing** (`mazegenerator`) package, which produces imperfect mazes from a given seed. The generation pipeline works as follows:

1. The external generator is called with the level's width/height from the config. **Level 1 always uses the `seed` value from the config file**, so its maze is identical every run. **From level 2 onward, a fresh random seed is drawn each time the level loads**, so those mazes are randomized on every playthrough and are not reproducible via the config seed.
2. The raw output (a grid encoded with bitflags for wall directions: 1=up, 2=right, 4=down, 8=left) is parsed into the internal grid at the target width/height.
3. Super-pacgums are placed in the 4 corners of the grid, regular pacgums fill every other non-wall cell, and the center cell (the player's spawn point) is cleared of items.

If the external generator is unavailable or fails for any reason, a fallback checkerboard-style grid is generated instead, and the same item-placement step is applied.

---

## Implementation

### Game loop

The game runs at a capped framerate (≈60 FPS via `SDL_Delay`). Each frame, SDL2 events are polled, then the appropriate display/compute function is called. Movement and collision resolution happen inside `GameEngine.update(delta_time)`, which is called only when the player has chosen a direction.

The game does not start moving until the player presses a directional key for the first time (`start` flag). This lets the player orient themselves before ghosts begin chasing.

### Movement system

Both Run-Man and ghosts use a **rail movement** system (`rail_movements` / `update_pos`): entities move toward a discrete grid destination cell, passing through the center of each cell to ensure clean directional changes. Speed is expressed in cells/frame and excess movement (overshoot) is carried over to the next movement phase.

### Ghost AI

- **Chase mode**: when within 10 cells (Manhattan distance), ghosts use BFS to find the shortest path to Run-Man. Beyond that range, they move randomly among valid directions (excluding U-turns).
- **Edible mode**: ghosts flee by choosing the direction that maximises their distance from Run-Man.
- **Dead mode**: ghosts freeze in their corner for 5 seconds before respawning in Chase mode.

### Collision detection

Collisions use a tolerance-based hitbox (±0.5 cell) on floating-point positions, allowing smooth detection even between grid cells.

### Sprite animation

Sprite sheets are used for Run-Man (4 directions × 5 frames + death animation) and ghosts (4 directions × 5 frames). Animation frames are advanced every 5 game ticks.

---

## General Software Architecture

```
src/
├── pac-man.py              # Entry point
├── engine/                 # Pure game logic (no display)
│   ├── config.py           # JSON config loader & validator
│   ├── engine.py           # GameEngine: coordinates all subsystems
│   ├── maze.py             # Maze generation, item placement, wall queries
│   ├── player.py           # Player state, direction, lives
│   ├── ghost.py            # Ghost state machine (Chase/Edible/Dead)
│   └── highscore.py        # Score persistence (read/write JSON)
├── display/                # SDL2 rendering layer
│   ├── display_base.py     # Shared rendering utilities (text, sprites, colors)
│   ├── display_game.py     # In-game rendering (maze, Run-Man, ghosts, HUD)
│   ├── display_ui.py       # Menu, pause, scores, instructions, end screen
│   ├── display.py          # Display = DisplayGame + DisplayUI (multiple inheritance)
│   └── helpers/
│       ├── textures.py     # SDL2 texture loader
│       └── sounds.py       # SDL2_mixer sound manager
└── inputs/
    ├── init_input_engine.py  # SDL2 safe init: window, renderer, fonts, sounds, textures via init_game()
    ├── input_sdl_engine.py   # Core event loop & state machine (menu → game → end)
    ├── input_process.py      # Key/mouse handlers per game state
    └── input_engine.py       # Entry point: ties InputProcesses + SDLCoreEngine together
```

### Key relationships

- `GameEngine` owns `Maze`, `Player`, `List[Ghost]`, `HighscoreManager`, and `GameConfig`. It exposes `update(delta_time)` and `get_state()`.
- `Display` inherits from both `DisplayGame` and `DisplayUI` (Python multiple inheritance), sharing the base renderer and texture dictionary from `BaseDisplay`.
- `InputEngine` inherits from both `InputProcesses` and `SDLCoreEngine`. `InputProcesses` (inheriting `InitInputEngine`) owns SDL2 resources, `GameEngine`, and all per-state key/mouse handlers. `SDLCoreEngine` runs the core event loop and state machine. `InitInputEngine` handles safe SDL2 initialization and resource cleanup via `init_game()`, with structured try/destroy/free chains.
- The engine layer has **no dependency** on SDL2 — it can be tested or reused independently.

---

## Cheat Mode

Cheat codes are entered via the in-game text input (press `/` to open, then type the command and press Enter):

| Command | Effect |
|---|---|
| `/cheat` | Enable invincibility (ghosts cannot kill Run-Man) and increase player speed by ×1.25 each time it's entered (repeatable, speed is capped at a maximum) |
| `/speed` | Instantly set player speed to a fixed fast value |
| `/slow` | Slightly decrease player speed (repeatable) |
| `/next` | Immediately skip to the next level |

These are designed to let peer reviewers quickly test all game features without playing through every level.

---

## Resources

### Documentation & References
- [SDL2 Python bindings (pysdl2)](https://pysdl2.readthedocs.io/)
- [SDL2 official documentation](https://wiki.libsdl.org/)
- [SDL keysym reference](https://www.libsdl.org/release/SDL-1.2.15/docs/html/sdlkey.html) — key symbol list, very useful for input handling
- [Real Pacman game reference](https://freepacman.org/)
- [FontSpace](https://www.fontspace.com/) — free fonts distributor ; fonts used : [Brookeshappell8](https://www.fontspace.com/brookeshappell8-font-f15898), [Shirtsy](https://www.fontspace.com/shirtsy-font-f7258), [Moon and Latte](https://www.fontspace.com/moon-and-latte-font-f164077)

### Tools
- [GIMP](https://www.gimp.org/) — used to create and edit all game graphics and sprites
- [Audacity](https://www.audacityteam.org/) — used to create and edit all game sounds

### AI Usage

AI (Claude, by Anthropic) was used during this project for the following tasks:
- Generating this README
- Explaining SDL2 best practices, internal workings, and available functions relevant to the display approach
- Describing best practices and tools for audio normalization with Audacity
- Researching solutions and debugging for the maze generation and game engine parts

All code was written and validated by the project authors. AI was not used to generate game logic autonomously.

---

## Project Management

The project was managed collaboratively between two contributors:

- **abenabde** — all files in `src/display/` and `src/inputs/`, the `update_pos` and `rail_movements` movement functions in `src/engine/engine.py`, and all game assets (graphics, sprites, fonts, sounds) in the `assets/` directory
- **ayhammou** — all remaining files in `src/engine/` (`config.py`, `engine.py` minus the two movement functions, `ghost.py`, `highscore.py`, `maze.py`, `player.py`)

Full project management documentation (timeline, risk analysis, team organization, testing plan) is available in the [`project_management/`](./project_management/) directory.
