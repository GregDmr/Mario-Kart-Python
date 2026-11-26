import pygame


class Checkpoint:
    """Zone rectangulaire à franchir (point de passage ou ligne d'arrivée) et position de réapparition associée"""

    def __init__(self, x: int, y: int, width: int, height: int, angle: float):
        """Crée la zone à partir de son coin haut gauche et de sa taille en pixels, angle de réapparition en degrés"""
        self.rect = pygame.Rect(x, y, width, height)
        self.angle = angle

    def contains(self, x: float, y: float) -> bool:
        """Indique si le point (x, y) est dans la zone"""
        return self.rect.collidepoint(x, y)

    def respawn_position(self) -> tuple[int, int, float]:
        """Position (x, y) et angle de réapparition : le centre de la zone"""
        return self.rect.centerx, self.rect.centery, self.angle
