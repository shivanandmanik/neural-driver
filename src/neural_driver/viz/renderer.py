import math

import pygame

from neural_driver.config import (
    AXIS_COLOR,
    BG_COLOR,
    CAR_COLOR,
    CAR_FRONT_COLOR,
    GRID_COLOR,
    GRID_LABEL_EVERY,
    GRID_SPACING,
    TEXT_COLOR,
)


class Renderer:
    """Draws the simulation onto a pygame surface. Owns no game state."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 22)  # pygame's built-in default font
        self.small_font = pygame.font.Font(None, 16)
        self.background = self._build_background()  # static, so drawn once and reused

    def draw(self, car):
        self.screen.blit(self.background, (0, 0))
        self.draw_car(car)
        self.draw_debug(car)

    def _build_background(self):
        """Background colour + grey grid every GRID_SPACING px + black x/y axes with pixel labels.
        Origin (0, 0) is the top-left corner: x grows right, y grows down."""
        width, height = self.screen.get_size()
        surface = pygame.Surface((width, height))
        surface.fill(BG_COLOR)

        for i, x in enumerate(range(GRID_SPACING, width, GRID_SPACING), start=1):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height))
            if i % GRID_LABEL_EVERY == 0:
                pygame.draw.line(surface, AXIS_COLOR, (x, 0), (x, 6), 2)  # tick
                surface.blit(self.small_font.render(str(x), True, TEXT_COLOR), (x + 3, 8))
        for i, y in enumerate(range(GRID_SPACING, height, GRID_SPACING), start=1):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y))
            if i % GRID_LABEL_EVERY == 0:
                pygame.draw.line(surface, AXIS_COLOR, (0, y), (6, y), 2)  # tick
                surface.blit(self.small_font.render(str(y), True, TEXT_COLOR), (9, y + 3))

        # Main axes along the top (x) and left (y) edges, since the origin is the top-left corner.
        pygame.draw.line(surface, AXIS_COLOR, (0, 1), (width, 1), 3)
        pygame.draw.line(surface, AXIS_COLOR, (1, 0), (1, height), 3)
        surface.blit(self.small_font.render("0", True, TEXT_COLOR), (6, 6))
        # Default font has no arrow glyphs, so plain labels.
        surface.blit(self.font.render("+x", True, AXIS_COLOR), (width - 30, 8))
        surface.blit(self.font.render("+y", True, AXIS_COLOR), (9, height - 50))
        return surface

    def draw_car(self, car):
        corners = car.corners()  # front-left, front-right, back-right, back-left
        pygame.draw.polygon(self.screen, CAR_COLOR, corners)
        pygame.draw.line(self.screen, CAR_FRONT_COLOR, corners[0], corners[1], 4)

    def draw_debug(self, car):
        text = (
            f"speed {car.speed:5.2f}   angle {math.degrees(car.angle) % 360:5.1f}°   "
            f"pos ({car.x:6.1f}, {car.y:6.1f})   [arrows/WASD drive, R reset, Esc quit]"
        )
        # Bottom-left, so it doesn't cover the x-axis labels along the top.
        _, height = self.screen.get_size()
        self.screen.blit(self.font.render(text, True, TEXT_COLOR), (40, height - 24))
