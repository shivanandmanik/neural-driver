import math

from neural_driver.config import (
    ACCELERATION,
    BRAKE,
    CAR_LENGTH,
    CAR_START_ANGLE,
    CAR_START_X,
    CAR_START_Y,
    CAR_WIDTH,
    FRICTION,
    MAX_REVERSE_SPEED,
    MAX_SPEED,
    SPEED_EPS,
    TURN_RATE,
)


class Car:
    def __init__(self, x=CAR_START_X, y=CAR_START_Y, angle=CAR_START_ANGLE):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)  # radians, 0 = facing +x
        self.speed = 0.0           # signed: negative = reversing
        self.length = CAR_LENGTH
        self.width = CAR_WIDTH

    def update(self, forward, reverse, left, right):
        """Advance one frame. Order matters: speed first, then turn, then move."""
        throttling = self._apply_throttle(forward, reverse)
        if not throttling:
            self._apply_friction()
        self._clamp_speed()
        self._steer(left, right)
        self._move()

    # --- one frame, broken into steps ---

    def _apply_throttle(self, forward, reverse):
        """forward: speed up. reverse: brake while moving forward, then reverse once stopped.
        Both or neither pressed = no throttle. Returns True if a throttle input was applied."""
        if forward == reverse:
            return False
        if forward:
            self.speed += ACCELERATION
        elif self.speed > SPEED_EPS:
            # Braking: stop at 0 rather than jumping straight into reverse this frame.
            # Snap float leftovers (e.g. 3.3e-16) to exactly 0.
            self.speed -= BRAKE
            if self.speed < SPEED_EPS:
                self.speed = 0.0
        else:
            self.speed -= ACCELERATION
        return True

    def _apply_friction(self):
        """Pull speed toward 0 by FRICTION; snap to exactly 0 instead of overshooting."""
        if abs(self.speed) <= FRICTION:
            self.speed = 0.0
        else:
            self.speed -= math.copysign(FRICTION, self.speed)

    def _clamp_speed(self):
        """Keep speed within [-MAX_REVERSE_SPEED, MAX_SPEED]."""
        self.speed = max(-MAX_REVERSE_SPEED, min(MAX_SPEED, self.speed))

    def _steer(self, left, right):
        """Change angle by a fixed TURN_RATE (not scaled by speed).
        No steering at speed 0; direction flips when reversing, like a real car."""
        if self.speed == 0:
            return
        direction = 1 if self.speed > 0 else -1
        # Pygame y points down, so +angle = clockwise = right turn.
        if right:
            self.angle += TURN_RATE * direction
        if left:
            self.angle -= TURN_RATE * direction

    def _move(self):
        """x += cos(angle) * speed, y += sin(angle) * speed."""
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    # --- geometry ---

    def corners(self):
        """Return the 4 corners of the rotated rectangle as [(x, y), ...] in order
        (front-left, front-right, back-right, back-left)."""
        cos_a, sin_a = math.cos(self.angle), math.sin(self.angle)
        # Half-vector pointing forward along the heading.
        fx, fy = cos_a * self.length / 2, sin_a * self.length / 2
        # Half-vector pointing to the car's right: heading rotated +90° (clockwise on screen).
        rx, ry = -sin_a * self.width / 2, cos_a * self.width / 2
        return [
            (self.x + fx - rx, self.y + fy - ry),  # front-left
            (self.x + fx + rx, self.y + fy + ry),  # front-right
            (self.x - fx + rx, self.y - fy + ry),  # back-right
            (self.x - fx - rx, self.y - fy - ry),  # back-left
        ]
