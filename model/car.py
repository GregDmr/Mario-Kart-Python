import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)


class Car:

    def __init__(self, start_col: int, start_row: int):
        """ Initialise une voiture à partir de sa position sur la grille """

        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2

        # Initialisation vitesse et angle 
        self.speed: float = 0.0
        self.angle: float = 0.0

        # Génération du sprite visuel de base 
        self.sprite = self.build_sprite()

    def accelerate(self) -> None:
        """ Augmente la vitesse de la voiture suivant la constante d'accélération"""
        self.speed += CAR_ACCELERATION

    def update_position(self) -> None:
        """ Met à jour la position de la voiture en fonction de sa vitesse"""
        self.y += self.speed

    def build_sprite(self) -> pygame.Surface:
        """ Construit et retourne la surface graphique (sprite) de la voiture """

        # Création d'une surface vide transparente avec alpha de la taille de la voiture
        surf = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)

        # Dessin de la voiture avec des bords arrondis
        pygame.draw.rect(surf, # Surface ou l'on dessine
                        (255, 0, 0), # Couleur de la voiture
                        (0, 0, CAR_WIDTH,CAR_HEIGHT), # Définition du rectangle géométrique (x, y, largeur, hauteur)
                        border_radius=5 # Rayons des coins arrondis
                        )

        # On retourne la surface graphique avec la voiture
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """ Calcule et retourne le sprite pivoté selon l'angle actuel ainsi que son rectangle centré positionné pour l'affichage """

        # Rotation de l'image de base (application de - pour tourner dans le sens horaire)
        rotated = pygame.transform.rotate(self.sprite, -self.angle)

        # Recalcule le rectangle de l'image en fixant son centre exact sur les coordonnées (x,y) de la voiture (indispensable car une rotation va modifier les dimensions globales de l'image)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))

        return rotated, rect
