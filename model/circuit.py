from model.road_tile import RoadTile
from constants import TILE_SIZE


class Circuit:

    def __init__(self,  grid: list[list[RoadTile]]):
        """ Initialisation du circuit à partir de la grille 2D des tuiles """
        self.grid = grid
        self.rows = len(grid) # Nombre total de lignes
        self.cols = len(grid[0]) if grid else 0 # Nombre total de colonnes

    def get_tile(self, col: int, row: int) -> RoadTile | None:
        """ Récupération d'une tuile, va servir à déterminer l'interaction voiture / sol """

        # On vérifie si la tuile est bien dans la matrice 2D
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None 

    def get_tile_at_pixel(self, px: float, py: float) -> RoadTile | None:
        """ Permet de récupérer la tuile correspondant à une coordonnée (x,y) """

        # On recalcule la cooordonnée de la tuile
        col = int(px // TILE_SIZE)
        row = int(py // TILE_SIZE)

        # On récupère la tuile associée à (x,y)
        return self.get_tile(col, row)

    def pixel_width(self) -> int:
        """ Calcule et retourne la largeur totale du circuit en pixels """
        return self.cols * TILE_SIZE

    def pixel_height(self) -> int:
        """ Calcule et retourne la hauteur totale du circuit en pixels """
        return self.rows * TILE_SIZE
