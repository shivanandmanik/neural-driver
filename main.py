import argparse

import pygame

from neural_driver.config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from neural_driver.env.car import Car
from neural_driver.viz.renderer import Renderer


def read_controls(keys):
    """Map the keyboard to Car.update(forward, reverse, left, right)."""
    return (
        keys[pygame.K_UP] or keys[pygame.K_w],
        keys[pygame.K_DOWN] or keys[pygame.K_s],
        keys[pygame.K_LEFT] or keys[pygame.K_a],
        keys[pygame.K_RIGHT] or keys[pygame.K_d],
    )


def run_drive():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Neural Driver - drive")
    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    car = Car()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    car = Car()

        car.update(*read_controls(pygame.key.get_pressed()))
        renderer.draw(car)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Neural Driver")
    # plan / train / watch modes arrive in later phases
    parser.add_argument("--mode", choices=["drive"], default="drive")
    args = parser.parse_args()

    if args.mode == "drive":
        run_drive()


if __name__ == "__main__":
    main()
