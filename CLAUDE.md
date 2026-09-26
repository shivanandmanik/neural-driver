# Neural Driver — project context for Claude

## What this project is
A car drives through a randomly generated 2D map full of fake gullies (dead ends) and passages.
**A\* plans** the optimal route; a **neural network drives** it without crashing, including on maps it has never seen.
Portfolio project for Shiv's pivot from Data Engineering to AI/ML engineering. Weekends only, ~16 weekends (3–4 months).

Full roadmap (source of truth for phases and checklists):
https://claude.ai/code/artifact/2011a7c7-cefd-49d7-8f46-799e91a9169d

## How to work with me (important)
- **I write the logic myself.** Explain concepts, give specs, hints, and test ideas. Do NOT write full implementations of
  car physics, A\*, geometry, sensors, the network, the genetic algorithm or fitness unless I explicitly ask for code.
- Boilerplate is fine to write when asked (pyproject, plotting, CLI wiring).
- Review my code when I paste it: point out bugs and edge cases, and ask guiding questions before giving fixes.
- Keep answers concise (3–5 sentences unless I ask for detail). Treat me as a peer. Numbers over generic advice.
- I'm on Windows + PowerShell.

## Design decisions (settled)
| Area | Decision |
|---|---|
| Stack | All Python 3.12: pygame-ce (sim + drawing), NumPy (sensors, network, GA), Matplotlib (charts), pytest |
| Packaging | `pyproject.toml`, src layout, `pip install -e ".[dev]"`; optional `rl` extra = gymnasium + stable-baselines3 |
| Separation | `env/`, `planning/`, `brain/` never import pygame. Only `viz/` and `main.py` do, so training runs headless |
| Env API | Gymnasium-style `reset()` / `step()` so PPO (Stable-Baselines3) can plug in later |
| Map | Seeded random maps: walls with real passages + fake gullies (U-shaped dead-end pockets) + random boulders. Grid walls first, then smooth variable-width roads |
| Planning | A\* on an occupancy grid (~4–8 px cells), obstacles inflated by car half-width + margin, 8-neighbour, octile heuristic, `heapq`. Path smoothed via line-of-sight pruning + Chaikin, then resampled |
| Driver | From-scratch NumPy MLP, ~10 → 12 → 4. Inputs: 7 ray distances (normalized 0–1), speed, angle + distance to a lookahead waypoint ~50 px ahead on the A\* path. Outputs: left, right, throttle, brake |
| Training | Neuroevolution: ~200 cars, elitism top 10%, Gaussian mutation (~0.1), optional crossover. New random map every generation (or score on 3 maps) to avoid memorizing |
| Fitness | Progress along the A\* path + goal bonus − crash penalty − idle penalty (kill after ~3 s without progress) |
| Baseline | Hand-written pure-pursuit controller; the trained network should beat it |
| Evaluation | Fixed 100-map seeded test set: success rate, crash rate, time to goal, deviation from path; ablation without waypoint inputs |
| Web demo | pygbag build (Phase 5) + GIFs in README |

## Conventions
- Angles in **radians**. Angle 0 = facing right (+x). Pygame y axis points **down**, so +angle turns clockwise = right turn.
- Movement: `x += cos(a) * speed`, `y += sin(a) * speed`. Speed is signed (negative = reversing).
- All tunable numbers live in `src/neural_driver/config.py` (UPPER_CASE constants).

## Structure (final target)
Repo root folder is named `neural-driver/` (the repo root is the project folder itself; no extra nesting).
```
neural-driver/
├── README.md
├── CLAUDE.md
├── pyproject.toml            # deps: pygame, numpy, matplotlib, pytest (+ gymnasium, stable-baselines3 later)
├── .gitignore
├── main.py                   # entry point: python main.py --mode drive | plan | train | watch
│
├── src/neural_driver/
│   ├── __init__.py
│   ├── config.py             # all constants: screen size, car size, speeds, ray count, GA settings
│   │
│   ├── env/                  # the simulation, with no drawing (runs headless)
│   │   ├── __init__.py
│   │   ├── car.py            # Car: position, angle, speed, update(controls), corners()
│   │   ├── geometry.py       # segment intersection, point-in-shape, rotation helpers
│   │   ├── map_gen.py        # seeded random maps: walls, passages, fake gullies, boulders
│   │   ├── sensors.py        # raycasts → normalized distances
│   │   ├── collision.py      # car vs walls
│   │   └── driving_env.py    # Gymnasium-style reset() / step() wrapping everything
│   │
│   ├── planning/             # A* side
│   │   ├── __init__.py
│   │   ├── grid.py           # occupancy grid + obstacle inflation
│   │   ├── astar.py          # A* with heapq
│   │   └── smoothing.py      # line-of-sight pruning + Chaikin + resampling
│   │
│   ├── brain/                # learning side
│   │   ├── __init__.py
│   │   ├── network.py        # NumPy MLP: forward(), to/from flat genome, save/load .npz
│   │   ├── genetic.py        # selection, elitism, mutation, crossover
│   │   └── fitness.py        # progress along A* path, goal bonus, crash/idle penalties
│   │
│   ├── baselines/
│   │   ├── __init__.py
│   │   └── pure_pursuit.py   # hand-written controller to beat
│   │
│   └── viz/                  # everything Pygame draws
│       ├── __init__.py
│       ├── renderer.py       # draws map, grid, path, cars, rays
│       ├── hud.py            # speed, generation, fitness text
│       └── editor.py         # draw your own obstacles with the mouse
│
├── scripts/
│   ├── train.py              # headless neuroevolution run → saves best model + fitness log
│   ├── evaluate.py           # runs a model on the 100-map test set → CSV
│   └── plot_results.py       # learning curve + benchmark charts
│
├── tests/
│   ├── test_car.py
│   ├── test_geometry.py
│   ├── test_astar.py
│   ├── test_sensors.py
│   └── test_network.py
│
├── models/                   # saved .npz networks (best_gen_050.npz …)
├── results/                  # CSVs and charts from evaluate / plot
├── docs/
│   ├── DEVLOG.md             # weekly notes: what broke, what you learned (great for interviews)
│   ├── roadmap.md            # full roadmap (offline copy) + NeuralDriver.html
│   └── media/                # GIFs for the README
└── web/                      # pygbag build, Phase 5
```
Only the files needed for the current step are created; add others as phases arrive.

## Current status
- Weekend 1 done (2026-09-27): `env/car.py` + 8 tests in `tests/test_car.py` passing, `viz/renderer.py`,
  `main.py --mode drive` (arrows/WASD, R reset). Bugs and design notes in `docs/DEVLOG.md`.
  Activate the venv first (`.venv\Scripts\Activate.ps1`); otherwise `python` is Anaconda's.
- **Next (Weekend 2, Phase 1):** drive it and tune ACCELERATION / TURN_RATE / FRICTION by feel, then map generator v1
  (grid of random walls, keep only maps where start→goal is connected via BFS) and collisions (car vs walls).
