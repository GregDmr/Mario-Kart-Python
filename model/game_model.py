from constants import GameState, GRID_ROWS, GRID_COLS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile


class GameModel:
    """ Représentation du modèle global du jeu """
    def __init__(self):
        """ Initialisation du modèle """
        self.state: str = GameState.MENU # Etat du jeu, menu par défaut
        self.circuit: Circuit | None = None # Référence vers le circuit actif
        self.car: Car | None = None # Référence vers la voiture du joueur

    def load_circuit(self) -> None:
        """ Charge et génère le circuit ainsi que les voitures """
        grid = [[RoadTile(col=col_idx, row=row_idx) for row_idx in range(GRID_COLS)] for col_idx in range(GRID_ROWS)]
        self.circuit = Circuit(grid=grid)
        self.spawn_car()

    def spawn_car(self) -> None:
        """ Fait apparaitre la voiture """
        self.car = Car(7, 1)

    def update(self) -> None:
        """ Fonction de mise à jour du jeu pendant la course """

        # Sécurité si le jeu n'est pas en cours de course ou si aucun circuit n'est chargé
        if self.state != GameState.RACING or self.circuit is None:
            return

        # Mise à jour de la position de la voiture et de ses propriétés internes
        self.car.update_position()
