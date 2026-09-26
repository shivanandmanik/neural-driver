# Dev log

## Weekend 1 (2026-09-27): project setup + car physics

**Built**
- Project skeleton: `pyproject.toml` (src layout, `dev` / `rl` extras), uv venv, `config.py` with all tunables.
- `env/car.py`: `Car(x, y, angle)` with `update(forward, reverse, left, right)` and `corners()`.
  One frame = throttle/brake → friction (only when coasting) → clamp → steer → move.
- `tests/test_car.py`: 8 tests (9 cases): acceleration, brake-then-reverse, both speed clamps,
  friction snap, no steering at rest, steering flip in reverse, movement along heading, corners at 0 and π/2.
- `viz/renderer.py` + `main.py --mode drive`: drive with arrows/WASD, R to reset, speed/angle readout.
  `env/` never imports pygame, so training can run headless later.

**Bugs and what I learned**
1. **`ModuleNotFoundError: neural_driver`** after renaming the folder. Two causes: venvs store absolute
   paths so they don't survive a move (recreated it), and the venv wasn't activated, so `python`
   was Anaconda's. Check with `(Get-Command python).Source`.
2. **Float leftovers in braking.** Braking from 3.0 by 0.3 left `3.3e-16` after 10 frames instead of 0,
   so the car spent an extra frame "braking" before it reversed. I considered rescaling everything to
   integers, but rejected it: position and angle come from sin/cos and stay floats anyway, and so will the
   network and the rays. Fix: `SPEED_EPS = 1e-9`, snap to exactly 0 after braking; tests use `pytest.approx`.
3. **My first epsilon fix broke reversing.** I added a branch "if |speed| < EPS: speed = 0" *before* the
   reverse branch, so a stopped car caught that branch every frame and could never back up. The
   brake-then-reverse test caught it (`speeds[11]` was 0.0, not −0.2). Lesson: put the snap inside the
   branch that causes the leftover, not as a separate case that shadows valid states.
4. **A test with no asserts passes.** My first test only printed speeds, so pytest reported green while
   bug 3 was live. Every test needs at least one assert that would fail if the behaviour broke.
5. **Copy-paste in a test.** `test_no_steering_when_stopped` pressed left twice, so "right at speed 0"
   was untested. Fixed to press left, then right.

**Design notes**
- The reverse key does double duty: brake while moving forward, reverse gear once stopped.
  Maps directly to the network's future `throttle` / `brake` outputs.
- `BRAKE` (0.3) > `ACCELERATION` (0.2) so stopping is quicker than speeding up.
- Steering doesn't scale with speed yet, and the angle isn't wrapped to [−π, π]. Revisit wrapping
  when computing "angle to waypoint" for the network.

**Next:** Weekend 2: tune the driving feel, then start random grid maps + collisions.
