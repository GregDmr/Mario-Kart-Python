import pygame
from constants import TILE_SIZE
from tools.track_converter import references

class RoadTile:
    """ Représentation d'une tuile individuelle """
    def __init__(self, col: int, row: int, road_type : int =0):
        """ Initialisation de la tuile"""
        self.col = col # Indice de la colonne
        self.row = row # Indice de la ligne 
        self.sprite: pygame.Surface | None = None # Stockage de l'image de la tuile
        self.road_type = road_type
    def get_sprite(self, tile_size: int = TILE_SIZE) -> pygame.Surface:
        """ Retourne le sprite graphique de la tuile """

        # Si le sprite existe et est à la bonne taille on le renvoie directement
        if self.sprite and self.sprite.get_width() == tile_size:
            return self.sprite

        # Création d'une surface vide de la taille d'une tuile
        surface = pygame.Surface((tile_size, tile_size))

        # On remplit cette surface d'une couleur en RGB
        surface.fill(references[self.road_type])
        r,g,b = references[self.road_type]
        # On dessine une bordure de 2 pixels autour de la tuile pour la visibilité
        pygame.draw.rect(surface, 
                        (max(0,r-10), max(0,g-10), max(0,b-10)), # Couleur en RGB
                        surface.get_rect(), # Dimension et position du rectangle
                        2 # Epaisseur de la ligne 
                        )
        #eventuellement : il faut egalement definir des propriétés de la tile (traction etc)
        # Sauvegarde de la représentation graphique de la tuile
        self.sprite = surface
        return self.sprite
        
       