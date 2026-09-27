# Neural Driver

A car drives through a randomly generated 2D map full of fake gullies (dead ends) and real passages.
**A\*** plans the optimal route; a **neural network**, trained by neuroevolution, drives it without
crashing, including on maps it has never seen.

Everything is built from scratch in Python: car physics, geometry, raycast sensors, A\*, the
neural network (NumPy) and the genetic algorithm. Pygame is used only for drawing, so training runs headless.

> **Status: Phase 1, in progress.** Car physics and keyboard driving work. Maps, collisions,
> sensors, A\* and the trained driver are coming. See the [roadmap](#roadmap).

## How it works (target design)

| Part | Approach |
|---|---|
| Map | Seeded random maps: walls with real passages, U-shaped fake gullies, random boulders |
| Planning | A\* on an occupancy grid, obstacles inflated by the car's half-width, 8-neighbour, octile heuristic; path smoothed and resampled |
| Driver | NumPy MLP (~10 → 12 → 4). Inputs: 7 ray distances, speed, angle + distance to a waypoint ~50 px ahead on the A\* path. Outputs: left, right, throttle, brake |
| Training | Neuroevolution: ~200 cars per generation, elitism, Gaussian mutation, a new random map every generation so it can't memorize one |
| Fitness | Progress along the A\* path + goal bonus − crash penalty − idle penalty |
| Evaluation | Fixed 100-map test set vs. a hand-written pure-pursuit baseline |

## Setup

Requires Python 3.12. Commands below are for Windows PowerShell.

```powershell
git clone https://github.com/shivanandmanik/neural-driver.git
cd neural-driver

# with uv (recommended)
uv venv --python 3.12
uv pip install -e ".[dev]"

# or with plain pip
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Activate the venv in every new terminal:

```powershell
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
```

If you get `ModuleNotFoundError: No module named 'neural_driver'`, the venv isn't active. Check with
`(Get-Command python).Source`, which should point inside `.venv`. If PowerShell blocks the activate script,
run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

## Usage

### Drive the car yourself

```powershell
python main.py              # same as: python main.py --mode drive
```

| Key | Action |
|---|---|
| ↑ / W | Accelerate |
| ↓ / S | Brake; once stopped, reverse |
| ← / A, → / D | Steer (only while moving; flips when reversing) |
| R | Reset the car |
| Esc | Quit |

The top-left readout shows speed, heading and position. There are no walls yet, so press R if you drive off-screen.

### Run the tests

```powershell
pytest                      # all tests
pytest tests/test_car.py -v # one file, verbose
```

### Tune the physics

All tunable numbers live in `src/neural_driver/config.py`: screen size, car size, `ACCELERATION`, `BRAKE`,
`MAX_SPEED`, `MAX_REVERSE_SPEED`, `FRICTION`, `TURN_RATE`. Units are pixels and radians per frame at 60 FPS.

## Project structure

```
neural-driver/
├── main.py                   # entry point: python main.py --mode drive
├── src/neural_driver/
│   ├── config.py             # all constants
│   ├── env/                  # simulation, no drawing (runs headless)
│   │   └── car.py            # Car: update(forward, reverse, left, right), corners()
│   └── viz/                  # everything pygame draws
│       └── renderer.py
├── tests/
│   └── test_car.py
└── docs/
    ├── DEVLOG.md             # weekly notes: what broke, what I learned
    └── roadmap.md            # full phase-by-phase plan
```

`env/`, `planning/` and `brain/` never import pygame; only `viz/` and `main.py` do.

Conventions: angles are in radians, and 0 means facing right (+x). The pygame y axis points down, so a positive angle change is a clockwise (right) turn. Speed is signed; negative means reversing.

## Roadmap

| Weekends | Phase | Milestone |
|---|---|---|
| 1–2 | 1 | Project setup, car physics, keyboard driving ✅ (tuning in progress) |
| 3–4 | 1 | Random grid maps → shapes with gullies; collisions; raycast sensors |
| 5–6 | 2 | A\* with obstacle inflation and path smoothing; explored cells visualized |
| 7–11 | 3–4 | NumPy network + genetic algorithm; training on a new random map each generation |
| 12–13 | 4 | 100-map benchmark, pure-pursuit baseline, ablation results |
| 15–16 | 5 | Browser demo (pygbag), GIFs, results write-up |

Details in [`docs/roadmap.md`](docs/roadmap.md); progress notes in [`docs/DEVLOG.md`](docs/DEVLOG.md).

## Tech stack

Python 3.12 · pygame-ce · NumPy · Matplotlib · pytest
