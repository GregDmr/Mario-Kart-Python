import random
import pygame
from controller.audio_controller import AudioController
import constants as c
from model.player import Player
import math

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

    def collision(self, player, audio_controller=None) -> None:
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
        Gestion collision entre itembox et kart uniquement (A FAIRE : rajouter collision avec greenshell par exemple pour faire disparaitre le cube)
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
            available_items = [Mushroom, Fake_ItemBox, Banana, GreenShell, BlueShell, Star, Bobomb]
            # Choix équiprobable entre les items de la liste 
            item_class = random.choice(available_items)
            # Attribution de l'item au joueur
            player.item = item_class()

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

    def collision(self, player, audio_controller=None) -> None:
        # Pas de collision prévue pour l'instant pour cette item 
        pass

    def use(self, player, audio_controller=None):
        """ Applique le boost du champignon avec un son """
        # Son
        if audio_controller:
            audio_controller.play_sound("kart_boost")

        player.car.boost()

class Fake_ItemBox(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_FAKE_ITEMBOX)
        self.name = "Fake_ItemBox"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

    def collision(self, player, audio_controller=None):
        # Activation de l'effet sur la voiture du joueur
        player.car.big_hit()

        # Bruitage du choc
        if audio_controller:
            audio_controller.play_sound("collision_rock") # A MODIFIER

        # Désactivation de l'item
        self.to_remove = True

    def use(self, player, audio_controller=None): 
        if audio_controller:
            audio_controller.play_sound("drop_fake_itembox")

        # Calcul des coordonnées ou on va drop le fake itembox
        dist = 40 # A ajuster plus tard suivant la taille de la voiture
        angle_rad = math.radians(player.car.angle)
        drop_x = player.car.x - dist * math.sin(angle_rad)
        drop_y = player.car.y - dist * math.cos(angle_rad)
        
        # On renvoie l'instance au GameModel
        return Fake_ItemBox(x=drop_x, y=drop_y)



class Banana(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_BANANA)
        self.name = "Banana"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

    def collision(self, player, audio_controller=None):
        # Activation de l'effet sur la voiture du joueur
        player.car.slide()
        
        # Bruitage du choc
        if audio_controller:
            audio_controller.play_sound("collision_rock") # A MODIFIER
        
        # Désactivation de l'item
        self.to_remove = True

    def use(self, player, audio_controller=None):
        if audio_controller:
            audio_controller.play_sound("drop_banana")

        # Calcul des coordonnées ou on va drop la banane
        dist = 40
        angle_rad = math.radians(player.car.angle)
        drop_x = player.car.x - dist * math.sin(angle_rad)
        drop_y = player.car.y - dist * math.cos(angle_rad)

        # On renvoie l'instance au GameModel
        return Banana(x=drop_x, y=drop_y)

class GreenShell(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_GREEN_SHELL)
        self.name = "GreenShell"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

        # Position et physique de base
        self.x = float(x)
        self.y = float(y)
        self.angle = 0.0
        self.speed = 12.0
        self.dir_x = 0.0
        self.dir_y = 0.0
        self.owner = None

        # Synchronisation du rectangle Pygame avec les coordonnées initiales
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        """ Déplacement en ligne droite """
        if not self.is_active:
            return

        # Déplacement frame par frame
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed

        # Synchronisation de la hitbox Pygame
        self.rect.center = (int(self.x), int(self.y))

        # Dès que la carapace ne touche plus le kart du lanceur, on retire l'immunité
        if self.owner and not self.rect.colliderect(self.owner.car.get_rect()):
            self.owner = None

    def collision(self, player, audio_controller=None):
        if not self.is_active:
            return

        # On ignore le choc si c'est encore le joueur qui vient de la lancer
        if player == self.owner:
            return

        # Effet sur le joueur touché
        player.car.big_hit()
                
        if audio_controller:
            audio_controller.play_sound("collision_rock")
                
        self.is_active = False
        self.to_remove = True

    def lancer(self, player):
        """ Initialise la trajectoire, la vitesse et la position devant le joueur """
        self.owner = player
        self.angle = player.car.angle
        
        # Vitesse de la carapace (vitesse du kart + bonus)
        car_speed = player.car.calcul_vitesse_abs()
        self.speed = max(6.0, car_speed + 2.0)

        # Calcul du vecteur direction selon l'angle du kart
        angle_rad = math.radians(self.angle)
        self.dir_x = math.sin(angle_rad)
        self.dir_y = math.cos(angle_rad)

        # Point d'apparition devant le kart 
        dist = 40
        self.x = player.car.x + dist * self.dir_x
        self.y = player.car.y + dist * self.dir_y

        # Placement immédiat du rect au point de spawn
        self.rect.center = (int(self.x), int(self.y))

    def use(self, player, audio_controller=None):
        if audio_controller:
            audio_controller.play_sound("drop_greenshell") # Effet sonore A MODIFIER

        shell = GreenShell()
        # Configuration tir
        shell.lancer(player)
        return shell 

class BlueShell(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_BLUE_SHELL)
        self.name = "BlueShell"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

    def collision(self, player, audio_controller=None):
        """ A FAIRE : Activer la collision uniquement si on touche le joueur, ignore collision avec les murs car objet volant"""
        # Activation de l'effet sur la voiture du joueur
        player.car.big_hit()
                
        # Bruitage du choc
        if audio_controller:
            audio_controller.play_sound("collision_wood") # A MODIFIER
                
        # Désactivation de l'item
        self.to_remove = True

    def use(self, player, audio_controller=None):
        if audio_controller:
            audio_controller.play_sound("drop_blueshell")

class Star(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_STAR)
        self.name = "Star"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))

    def collision(self, player, audio_controller=None):
        # Pas de collision prévue pour cette item car jamais sur le circuit directement, active un état spécial pour le joueur
        pass

    def use(self, player, audio_controller=None):
        if audio_controller:
            audio_controller.play_sound("use_star")

class Bobomb(Item):
    def __init__(self, x: float = 0, y: float = 0, track_size: int = 32, icon_size: int = 64):
        super().__init__(x, y, size=track_size, image_path=c.SPRITE_BOBOMB)
        self.name = "Bobomb"
        # Redimensionnement de l'icone pour le HUD
        self.icon = pygame.transform.scale(self.image, (icon_size, icon_size))
        
    def collision(self, player, audio_controller=None):
        # Activation de l'effet sur la voiture du joueur
        player.car.big_hit()
            
        # Bruitage du choc
        if audio_controller:
            audio_controller.play_sound("explosion_bomb")  
            
        # Désactivation de l'item
        self.to_remove = True
        
    def use(self, player, audio_controller=None):
        """ Ajouter timer pour explosion"""
        if audio_controller:
            audio_controller.play_sound("drop_fake_itembox")
            
        # Calcul des coordonnées ou on va drop la bombe
        dist = 40
        angle_rad = math.radians(player.car.angle)
        drop_x = player.car.x - dist * math.sin(angle_rad)
        drop_y = player.car.y - dist * math.cos(angle_rad)
            
        # On renvoie l'instance au GameModel
        return Bobomb(x=drop_x, y=drop_y)
