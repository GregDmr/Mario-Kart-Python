from constants import GameState, GRID_ROWS, GRID_COLS,WINDOW_HEIGHT,WINDOW_WIDTH, DEFAULT_KEYBINDS
from model.car import Car
from model.player import Player
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.menu import Menu, MainMenu, TrackMenu, PauseMenu, ResultsMenu, texture_path
from pygame.image import load
from pygame.transform import scale
from model.item import ItemBox

class GameModel:
    """ Représentation du modèle global du jeu """
    def __init__(self):
        """ Initialisation du modèle """
        self.state: str = GameState.MENU # Etat du jeu, menu par défaut
        self.circuit: Circuit | None = None # Référence vers le circuit actif
        self.players: list[Player] = [] # Joueurs de la course en cours
        self.cars: list[Car] = [] # Voitures de la course en cours
        #copie : modifier une touche ne doit pas modifier DEFAULT_KEYBINDS
        self.keybinds = [{action: list(keys) for action, keys in player_keys.items()} for player_keys in DEFAULT_KEYBINDS]
        self.items = [] # Liste des items présents sur la piste
        self.pending_track: str | None = None  #Circuit choisi, chargé pendant l'écran de chargement

        # Un menu par état qui en a un
        self.menus: dict[str, Menu] = {
            GameState.MENU: MainMenu(self),
            GameState.TRACK_SELECT: TrackMenu(self),
            GameState.PAUSE: PauseMenu(self),
            GameState.RESULTS: ResultsMenu(self),
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

    def restart_race(self):
        """Relance la course sur le circuit déjà chargé, sans le reconvertir"""
        self.spawn_players()
        self.items = list(self.circuit.item_boxes)
        for item in self.items:
            item.is_active = True
        self.change_state(GameState.RACING)

    def load_circuit(self, json_track_path: str) -> None:
        """Charge le circuit depuis son fichier JSON, prépare le rendu et fait spawner les entités."""

        # Instanciation du Circuit 
        self.circuit = Circuit(json_track_path)

        # Rendu de la texture visuelle pour l'affichage Pygame
        self.circuit_texture_render = load(self.circuit.texture_path).convert_alpha()
        self.circuit_texture_render = scale(self.circuit_texture_render, (WINDOW_WIDTH, WINDOW_HEIGHT))

        # Récupération des cubes d'items chargés par le circuit
        self.items = self.circuit.item_boxes

        # Instanciation karts et joueurs
        self.spawn_players()

    def spawn_players(self) -> None:
        """Fait apparaître les karts des joueurs à partir des positions fournies"""

        # Nettoyage des listes joueur et voiture au début de la partie
        self.players.clear()
        self.cars.clear()

        # On parcourt les positions définies dans la configuration du circuit
        #temp for testing :
        CHOSEN_CARS = [1,3]
        for index, spawn in enumerate(self.circuit.starting_positions):
            x = spawn["x"]
            y = spawn["y"]
            angle = spawn.get("angle", 90)

            # Instanciation de la voiture et du joueur associés
            car = Car(self.circuit, x, y, CHOSEN_CARS[index], angle)
            player = Player(index, car)

            self.cars.append(car)
            self.players.append(player)

    def update(self, audio_controller=None) -> None:
        """ Fonction de mise à jour du jeu pendant la course """

        # Sécurité si le jeu n'est pas en cours de course ou si aucun circuit n'est chargé
        if self.state != GameState.RACING or self.circuit is None:
            return
        # Mise à jour de la position de la voiture et de ses propriétés internes
        for player in self.players:
            player.car.update_position()
            player.update_progress(self.circuit)
            if player.laps >= self.circuit.laps:
                self.finish_race(player)
                return

        # Gestion des objets (réapparition + collisions + objets drop au sol)
        for item in self.items:
            # Vérifie si le délai de 3 secondes est écoulé pour faire réapparaître l'objet
            item.update()

            # Collision uniquement si l'objet est actif et qu'il touche la voiture
            for player in self.players:
                if item.is_active and player.car.get_rect().colliderect(item.rect):
                    item.collision(player, audio_controller)

        # Nettoyage de la liste d'items suivant le booléen to_remove
        self.items = [item for item in self.items if not item.to_remove]

    def finish_race(self, winner: Player) -> None:
        """Termine la course et affiche l'écran de fin avec le nom du vainqueur"""
        self.menus[GameState.RESULTS].title = f"{winner.name} gagne !"
        self.change_state(GameState.RESULTS)

    def respawn(self, player_index: int) -> None:
        """Replace la voiture du joueur au dernier point de passage qu'il a franchi"""
        self.players[player_index].respawn()

    def use_item(self, player_index: int, audio_controller=None) -> None:
        """ Le joueur utilise son objet (à compléter avec les objets) """
        player = self.players[player_index]
        if player.item is None:
            return

        # On récupère l'item utilisé par le jour pour savoir si on doit le déposer sur la piste
        drop_item = player.use_item(audio_controller)
        if drop_item is not None:
            self.items.append(drop_item)