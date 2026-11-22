import random
import pygame
from controller.audio_controller import AudioController
import constants as c
from model.player import Player

class Item:
    """
    Classe mère de tous les items présents sur la piste
    """

    def __init__(self, x: float, y: float, size: int = 32, image_path=None):
        # Booléens pour gérer l'état de l'item
        self.is_active = True  # Visibilité ou interaction sur la piste
        self.to_remove = False  # Indique si l'objet doit être détruit ou non
        self.icon = None # Icone pour l'affichage HUD

        # Chargement et redimensionnement du sprite
        try:
            raw_img = pygame.image.load(str(image_path)).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (size, size))
        except Exception as e:
            # Pour le debug (A RETIRER). On part du principe que tous les sprites sont présents
            print(f"Erreur sur le chargement du sprite de la classe {self.__class__.__name__}: {e}")
            self.image = pygame.Surface((size, size))

        # Création et centrage du rectangle en une seule ligne
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def collision(self, car, audio_controller=None) -> None:
        """ 
        Fonction de gestion des collisions.
        A surcharger obligatoirement dans les sous classes.
        """
        raise NotImplementedError(f"La méthode collision doit être implémentée dans {self.__class__.__name__}")

    def update(self) -> None:
        """ 
        Fonction de gestion des booléens.
        A surcharger dans les sous classes.
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        # On dessine uniquement les items actifs
        if self.is_active:
            surface.blit(self.image, self.rect.topleft)
            # Affichage hitbox poru debug
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

class ItemBox(Item):
    """
    Gestion des ItemBox avec distribution d'un item au joueur
    """

    def __init__(self, x: float, y: float, size: int = 32):
        # Initialisation et positionnement via la classe mère Item
        super().__init__(x, y, size, image_path=c.SPRITE_ITEMBOX)
        
        self.respawn_delay: int = 5000  # Temps avant réapparition (en ms)
        self.respawn_time: int = 0      # Timestamp de la prochaine réapparition

    def collision(self, player=None, audio_controller=None) -> None:
        """
        Gestion collision entre itembox et kart uniquement (rajouter collision avec greenshell par exemple pour faire disparaitre le cube)
        """
        # On ignore la collision si cube inactif
        if not self.is_active:
            return

        # Si le joueur n'a pas d'item
        if player.item is None:
            # On lui donne un item aléatoirement
            self.give_random_item(player)
            if audio_controller:
                    # On joue le son qui casse le cube et donne un item
                    audio_controller.play_sound("get_item")
        # Si le joueur a déjà un item
        else:
            if audio_controller:
                # On joue le son du cube qui se casse uniquement
                audio_controller.play_sound("break_itembox")
                
        # On passe le cube en inactif
        self.is_active = False
        
        # Démarrage chrono pour la réapparition
        self.respawn_time = pygame.time.get_ticks() + self.respawn_delay

    def give_random_item(self, player):
        """ Gestion du don d'objet au joueur"""
        # Test en donnant obligatoirement un champignon (A MODIFIER)
        if player.item is None:
            player.item = Mushroom()

    def update(self) -> None:
        """
        Vérifie si le temps d'attente est écoulé pour faire réapparaître le cube.
        """
        if not self.is_active:
            current_time = pygame.time.get_ticks()
            if current_time >= self.respawn_time:
                self.is_active = True

class Mushroom(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        # Initialisation avec la classe mère Item
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_MUSHROOM)
        self.name = "Mushroom"
        
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

    def collision(self, car, audio_controller=None) -> None:
        """Un champignon en inventaire n'a pas de collision physique au sol. A implémenter ensuite"""
        pass

    def use(self, player, audio_controller=None):
        """ Applique le boost du champignon avec un son """
        # Son
        if audio_controller:
            audio_controller.play_sound("kart_boost")

        # Rajouter l'accélération
        pass

class Fake_ItemBox(Item):
    def __init__(self, x, y, size=32):
        super().__init__(x, y, size, image_path=c.SPRITE_FAKE_ITEMBOX)

class Banana(Item):
    def __init__(self, x, y, size=32):
        super().__init__(x, y, size, image_path=c.SPRITE_BANANA)

class GreenShell(Item):
    pass