from constants import GameState, GRID_ROWS, GRID_COLS,WINDOW_HEIGHT,WINDOW_WIDTH
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.menu import Menu, MainMenu, TrackMenu, PauseMenu, texture_path
from tools.track_converter import convert_track
from pygame.image import load
from pygame.transform import scale
from model.item import ItemBox

class GameModel:
    """ Représentation du modèle global du jeu """
    def __init__(self):
        """ Initialisation du modèle """
        self.state: str = GameState.MENU # Etat du jeu, menu par défaut
        self.circuit: Circuit | None = None # Référence vers le circuit actif
        self.car: Car | None = None # Référence vers la voiture du joueur
        self.items = [] # Liste des cubes présents sur la piste
        self.pending_track: str | None = None  #Circuit choisi, chargé pendant l'écran de chargement

        # Un menu par état qui en a un
        self.menus: dict[str, Menu] = {
            GameState.MENU: MainMenu(self),
            GameState.TRACK_SELECT: TrackMenu(self),
            GameState.PAUSE: PauseMenu(self),
        }

    def current_menu(self):
        """Menu de l'état courant, ou None """
        return self.menus.get(self.state)  #get renvoie None si l'état n'a pas de menu (ex : RACING)

    def change_state(self, new_state: str):
        """Change d'écran """
        self.state = new_state
        if new_state == GameState.PAUSE:  #La pause s'ouvre toujours sur "Reprendre"
            self.menus[GameState.PAUSE].selected = 0

    def prepare_race(self, track_path: str):
        """Retient le circuit choisi et passe à l'écran de chargement"""
        self.pending_track = track_path
        self.change_state(GameState.LOADING)

    def start_race(self):
        """Charge le circuit retenu et lance la course"""
        self.load_circuit(self.pending_track)
        self.change_state(GameState.RACING)

    def load_circuit(self, track_path: str) -> None:
        """ Charge et génère le circuit ainsi que les voitures """
        type_grid = convert_track(track_path)

        self.circuit_texture_render = load(texture_path(track_path)).convert_alpha()
        self.circuit_texture_render = scale(self.circuit_texture_render, (WINDOW_WIDTH,WINDOW_HEIGHT)) #Changements importans ici pour choisir la bonne track
        grid = [[RoadTile(col=col_idx, row=row_idx, road_type=type_grid[row_idx][col_idx])for col_idx in range(GRID_COLS)] for row_idx in range(GRID_ROWS)]
        self.circuit = Circuit(grid=grid)
        self.spawn_car() # ici on modifie si on veut choisir le modele
        self.spawn_cubes()

    def spawn_car(self) -> None:
        """ Fait apparaitre la voiture """
        self.car = Car(self.circuit,200, 200,0)

    def spawn_cubes(self) -> None:
        "Fait apparaitre les cubes sur la piste"
        self.items = [ItemBox(436,152), ItemBox(1302,418), ItemBox(910,698)]

    def update(self, audio_controller=None) -> None:
        """ Fonction de mise à jour du jeu pendant la course """

        # Sécurité si le jeu n'est pas en cours de course ou si aucun circuit n'est chargé
        if self.state != GameState.RACING or self.circuit is None:
            return
        # Mise à jour de la position de la voiture et de ses propriétés internes
        self.car.update_position()

        # Gestion des objets (réapparition + collisions)
        for item in self.items:
            # Vérifie si le délai de 3 secondes est écoulé pour faire réapparaître l'objet
            item.update()

            # Collision uniquement si l'objet est actif et qu'il touche la voiture
            if item.is_active and self.car.get_rect().colliderect(item.rect):
                item.collision(self.car, audio_controller)
