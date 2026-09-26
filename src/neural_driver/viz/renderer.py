import math

import pygame

from neural_driver.config import BG_COLOR, CAR_COLOR, CAR_FRONT_COLOR, TEXT_COLOR


class Renderer:
    """Draws the simulation onto a pygame surface. Owns no game state."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 22)  # pygame's built-in default font

    def draw(self, car):
        self.screen.fill(BG_COLOR)
        self.draw_car(car)
        self.draw_debug(car)

    def draw_car(self, car):
        corners = car.corners()  # front-left, front-right, back-right, back-left
        pygame.draw.polygon(self.screen, CAR_COLOR, corners)
        pygame.draw.line(self.screen, CAR_FRONT_COLOR, corners[0], corners[1], 4)

    def draw_debug(self, car):
        text = (
            f"speed {car.speed:5.2f}   angle {math.degrees(car.angle) % 360:5.1f}°   "
            f"pos ({car.x:6.1f}, {car.y:6.1f})   [arrows/WASD drive, R reset, Esc quit]"
        )
        self.screen.blit(self.font.render(text, True, TEXT_COLOR), (10, 10))
