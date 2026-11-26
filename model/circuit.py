from model.road_tile import RoadTile
from constants import TILE_SIZE
import json 
import os
from tools.track_converter import convert_track
from model.item import ItemBox


class Circuit:

    def __init__(self, json_path: str):
        """Initialisation du circuit à partir de son fichier JSON de configuration"""
        self.json_path = json_path

        # Lecture du fichier JSON
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.track_id = config.get("track_id")
        self.name = config.get("track_name", "Circuit")
        self.starting_positions = config.get("starting_positions", [])
        
        # Instanciation immédiate des ItemBox depuis les coordonnées du JSON
        self.item_boxes = [
            ItemBox(x=box["x"], y=box["y"]) 
            for box in config.get("item_boxes", [])
        ]

        # Reconstitution du chemin d'accès à l'image PNG de la texture
        track_dir = os.path.dirname(json_path)
        self.texture_path = os.path.join(track_dir, f"{self.name}.png")

        # La grille est lue sur l'image layout (couleurs unies), pas sur la texture
        layout_path = os.path.join(track_dir, f"{self.name}_layout.png")
        type_grid = convert_track(layout_path)

        # Conversion en matrice 2D d'objets RoadTile
        self.grid: list[list[RoadTile]] = [
            [
                RoadTile(col=col_idx, row=row_idx, road_type=type_grid[row_idx][col_idx])
                for col_idx in range(len(type_grid[0]))
            ]
            for row_idx in range(len(type_grid))
        ]

        # Conversion de l'image PNG en grille 2D de RoadTile
        self.rows = len(self.grid) if self.grid else 0
        self.cols = len(self.grid[0]) if self.grid else 0

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
