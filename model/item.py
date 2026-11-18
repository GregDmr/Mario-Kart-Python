import random
import pygame
from controller.audio_controller import AudioController

# Faire une classe mère Item pour les objets de la piste avec les méthodes collisions etc


class ItemBox:
    def __init__(self, x: float, y: float, size=32):
        # Hitbox et positionnement (On initialise la zone géométrique puis on centre le rectangle aux coordonnées (x, y))
        self.rect = pygame.Rect(x, y, size, size)
        self.rect.center = (int(x), int(y))   

        # Gestion de l'état du cube
        self.is_active = True           # Définit sa présence ou non sur le circuit
        self.respawn_delay = 5000 # Temps d'attente avant la réapparition (en ms)

        # Chargement du sprite de l'item box et redimensionnement (convert_alpha() optimise le rendu avec transparence dans Pygame)
        raw_image_itembox = pygame.image.load("assets/items/sprite_cube.png").convert_alpha()
        self.image_itembox = pygame.transform.scale(raw_image_itembox, (size, size))

    def collision(self, car, audio_controller=None) -> None:
        """ Gère la collision avec le kart """
        # Cube déjà récupéré
        if not self.is_active:
            return

        # Désactivation du cube 
        self.is_active = False

        # Lecture du son 
        if audio_controller:
            audio_controller.play_sound("get_item")

        # Temps avant la réapparition
        self.respawn_time = pygame.time.get_ticks() + self.respawn_delay

        # Rajouter la transmission de l'item au joueur après une sélection aléatoire

    def update(self) -> None:
        """ Vérifie si le délai est écoulé pour faire réapparaître le cube """
        # On vérifie si le cube est bien désactivé et si le temps nécessaire est écoulé
        if not self.is_active:
            current_time = pygame.time.get_ticks()
            if current_time >= self.respawn_time:
                # Réactivation du cube
                self.is_active = True
    
    def draw(self, surface: pygame.Surface) -> None:
        """ Affiche le sprite réduit aux coordonnées du rectangle """
        if self.is_active: 
            surface.blit(self.image_itembox, self.rect.topleft)
            # Affichage du contour de la hitbox pour debug (A RETIRER ENSUITE)
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)