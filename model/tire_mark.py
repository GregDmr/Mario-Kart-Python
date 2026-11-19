import pygame

class TireMark :

    def __init__(self, posx, posy, lifespan):
        self.lifespan = lifespan
        self.lifespan_init = lifespan
        self.sprite = pygame.Surface((3, 3), pygame.SRCALPHA) #3 px = 0.3 m, largeur d'une roue
        self.sprite.fill((10, 10, 10))
        self.rect = self.sprite.get_rect(center=(posx, posy))
        
    def mark_sprite(self):
        return self.sprite, self.rect


    def lifespan_decount(self):
        self.lifespan -= 1