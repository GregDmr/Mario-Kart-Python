import pygame
import math
import os
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)


class Car:

    def __init__(self, start_col: int, start_row: int, chosen_car : int =0):
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2
        self.speed: float = 0.0
        self.angle: float = 0.0
        self.sprite = self.build_sprite(chosen_car)

    def accelerate(self) -> None:
        self.speed += CAR_ACCELERATION

    def update_position(self) -> None:
        self.y += self.speed

    def build_sprite(self, chosen_car) -> pygame.Surface:
        #surf = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        directory = "assets/sprites/cars"
        files = []
        for name in sorted(os.listdir(directory)):
            if name.endswith(".png"):
                path = os.path.join(directory, name)
                files.append(path)
        chosen_sprite = pygame.image.load(files[chosen_car]).convert_alpha() #sprite a la bonne taille
        chosen_sprite = pygame.transform.scale(chosen_sprite,(CAR_WIDTH,CAR_HEIGHT))

        #pygame.draw.rect(surf, (255, 0, 0), (0, 0, CAR_WIDTH,
                        # CAR_HEIGHT), border_radius=5)
        return chosen_sprite

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        rotated = pygame.transform.rotate(self.sprite, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect
