import pygame
import math
import os
import constants as c


class Car:

    def __init__(self, start_col: int, start_row: int, chosen_car : int =0):
        """ Initialise une voiture à partir de sa position sur la grille """

        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * c.TILE_SIZE + c.TILE_SIZE // 2
        self.y = start_row * c.TILE_SIZE + c.TILE_SIZE // 2

        # Initialisation vitesse et angle 
        self.speed: float = 0.0
        self.angle: float = 0.0

        # Génération du sprite visuel de base 
        self.sprite = self.build_sprite(chosen_car)

    def accelerate(self) -> None:
        """ Augmente la vitesse de la voiture suivant la constante d'accélération"""
        self.speed += c.CAR_ACCELERATION

        # Limitation de la vitesse de la voiture à MAX_SPEED
        if self.speed > c.MAX_SPEED:
            self.speed = c.MAX_SPEED

    def decelerate(self) -> None:
        """ Réduit la vitesse de la voiture, prend en compte le freinage ou la marche arrière"""
        if self.speed > 0:
            # La voiture avance : on applique uniquement le frein
            self.speed -= c.CAR_BRAKE
            
            # Si le freinage fait passer la vitesse en négatif, on s'arrête net à 0 pour la transition avec la marche arrière
            if self.speed < 0:
                self.speed = 0.0
                
        else:
            # Voiture à l'arrêt ou en vitesse négative : on applique la marche arrière
            self.speed -= c.CAR_REVERSE
            
            # Limitation de la vitesse maximale en marche arrière
            if self.speed < -c.MAX_REVERSE_SPEED:
                self.speed = -c.MAX_REVERSE_SPEED

    def friction(self) -> None:
        """ Applique les frottements pour ralentir la voiture dans le sens opposé à sa direction actuel"""
        if self.speed > 0:
            self.speed -= c.CAR_FRICTION
            if self.speed < 0:
                self.speed = 0.0
        elif self.speed < 0:
            self.speed += c.CAR_FRICTION
            if self.speed > 0:
                self.speed = 0

    def update_position(self) -> None:
        """ Met à jour la position de la voiture en fonction de sa vitesse"""
        self.y += self.speed

    def build_sprite(self, chosen_car) -> pygame.Surface:
        """ Construit et retourne la surface graphique (sprite) de la voiture """
        
        directory = "assets/sprites/cars"
        files = []
        for name in sorted(os.listdir(directory)):
            if name.endswith(".png"):
                path = os.path.join(directory, name)
                files.append(path)
        chosen_sprite = pygame.image.load(files[chosen_car]).convert_alpha() #sprite a la bonne taille
        chosen_sprite = pygame.transform.scale(chosen_sprite,(c.CAR_WIDTH,c.CAR_HEIGHT))
        return chosen_sprite

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """ Calcule et retourne le sprite pivoté selon l'angle actuel ainsi que son rectangle centré positionné pour l'affichage """

        # Rotation de l'image de base (application de - pour tourner dans le sens horaire)
        rotated = pygame.transform.rotate(self.sprite, -self.angle)

        # Recalcule le rectangle de l'image en fixant son centre exact sur les coordonnées (x,y) de la voiture (indispensable car une rotation va modifier les dimensions globales de l'image)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))

        return rotated, rect
