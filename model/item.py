import random
import pygame

class ItemBox:
    def __init__(self, x: float, y: float, size=32):
        self.rect = pygame.Rect(x, y, size, size)
        self.is_active = True # Définit si le cube est actif ou déjà récupéré
        self.respawn_delay = 5000 # (en ms)
        raw_image_itembox = pygame.image.load("assets/items/sprite_cube.png").convert_alpha()
        self.image_itembox = pygame.transform.scale(raw_image_itembox, (size, size))

    def on_collision(self, car) -> None:
        """ Gère la collision avec le kart """
        if not self.is_active:
            return

        self.is_active = False
        self.respawn_time = pygame.time.get_ticks() + self.respawn_delay

    def update(self) -> None:
        """ Vérifie si le délai est écoulé pour faire réapparaître le cube """
        if not self.is_active:
            current_time = pygame.time.get_ticks()
            if current_time >= self.respawn_time:
                self.is_active = True
    
    def draw(self, surface: pygame.Surface) -> None:
        """ Affiche le sprite réduit aux coordonnées du rectangle """
        if self.is_active: 
            surface.blit(self.image_itembox, self.rect.topleft)