import math

import pytest

from neural_driver.config import FRICTION, MAX_REVERSE_SPEED, MAX_SPEED, TURN_RATE
from neural_driver.env.car import Car


def test_brake_then_reverse():
    car = Car(0, 0, 0)
    car.speed = 3.0
    speeds = [car.speed]
    for _ in range(12):
        car.update(False, True, False, False)
        speeds.append(car.speed)
    assert speeds[10] == pytest.approx(0.0)
    assert speeds[11] == pytest.approx(-0.2)
    assert speeds[12] == pytest.approx(-0.4)


def test_accelerate_from_rest():
    car = Car(0, 0, 0)
    speeds = [car.speed]
    for _ in range(100):
        car.update(True, False, False, False)
        speeds.append(car.speed)
    assert speeds[1] == pytest.approx(0.2)
    assert speeds[10] == pytest.approx(2.0)
    assert speeds[100] == pytest.approx(MAX_SPEED)


def test_reverse_speed_is_clamped():
    car = Car(0, 0, 0)
    for _ in range(100):
        car.update(False, True, False, False)
    assert car.speed == pytest.approx(-MAX_REVERSE_SPEED)


def test_friction_snaps_to_exactly_zero():
    car = Car(0, 0, 0)
    car.speed = 1.0
    for _ in range(int(1.0 / FRICTION) + 5):
        car.update(False, False, False, False)
        assert car.speed >= 0.0  # friction must never push the car into reverse
    assert car.speed == 0.0  # exact, not approx: the snap is the point


def test_no_steering_when_stopped():
    car = Car(0, 0, 0)
    car.update(False, False, True, False)
    car.update(False, False, False, True)
    assert car.angle == 0.0


def test_steering_flips_when_reversing():
    forward_car = Car(0, 0, 0)
    forward_car.speed = 2.0
    forward_car.update(False, False, False, True)
    assert forward_car.angle == pytest.approx(TURN_RATE)  # right = clockwise = +angle

    reversing_car = Car(0, 0, 0)
    reversing_car.speed = -2.0
    reversing_car.update(False, False, False, True)
    assert reversing_car.angle == pytest.approx(-TURN_RATE)


def test_moves_along_heading():
    car = Car(0, 0, math.pi / 2)  # facing down the screen (+y)
    car.speed = 2.0
    car.update(False, False, False, False)
    assert car.x == pytest.approx(0.0, abs=1e-9)
    assert car.y == pytest.approx(2.0 - FRICTION)


@pytest.mark.parametrize(
    "angle, expected",
    [
        # facing right: front is +x, car's right side is +y (down)
        (0.0, [(20, -10), (20, 10), (-20, 10), (-20, -10)]),
        # facing down: front is +y, car's right side is -x
        (math.pi / 2, [(10, 20), (-10, 20), (-10, -20), (10, -20)]),
    ],
)
def test_corners(angle, expected):
    car = Car(0, 0, angle)  # CAR_LENGTH=40, CAR_WIDTH=20
    for (x, y), (ex, ey) in zip(car.corners(), expected):
        assert x == pytest.approx(ex, abs=1e-9)
        assert y == pytest.approx(ey, abs=1e-9)
