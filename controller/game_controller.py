import pygame
import sys
import constants as c
from model.game_model import GameModel
from view.game_view import GameView
from controller.input_handler import InputHandler
from controller.audio_controller import AudioController

UP_KEYS = (pygame.K_UP, pygame.K_z)  #Les deux joueurs peuvent naviguer dans les menus
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)


class GameController:

    def __init__(self):
        """ Constructeur de la classe GameController """

        self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SCALED | pygame.RESIZABLE) # Création de la fenêtre graphique (SCALED : l'image s'adapte à la taille de la fenêtre)
        self.clock = pygame.time.Clock() # Initialisation de l'horloge interne du jeu
        self.model = GameModel() # Instanciation de notre classe GameModel
        self.view = GameView(self.screen) # Connexion entre la partie graphique et la fenêtre de l'écran
        self.input_handlers = [InputHandler(keybinds) for keybinds in self.model.keybinds] # Initialisation du module pour gérer les entrées de  l'utilisateur
        self.audio_handler = AudioController(self.model) #Il faut passer le modele pour que le controle de la musique sache l'etat du jeu.
        self.running = True # Booléen qui maintient la boucle du jeu active

    def run(self) -> None:
        """ Boucle principale du jeu (tourne en continu à chaque frame) """

        while self.running:
            self.handle_events() # Récupération des actions
            self.update() # Mise à jour de la logique ainsi que la position des éléments
            self.render() # Redessine tout à l'écran
            self.music()
            self.clock.tick(c.FPS) # Régulation de la vitesse d'affichage du jeu

    def handle_events(self) -> None:
        """ Analyse de tous les évènements depuis la frame précédente """

        # Itération sur les événements enregistrés depuis la frame précédente (clics, touches, fermeture de fenêtre...)
        for event in pygame.event.get():
            # Si l'utilisateur quitte la fenêtre par la croix rouge
            if event.type == pygame.QUIT:
                self.quit() # Execution de la méthode de sortie de jeu
            # Gestion des autres évènements si on appuie sur une touche
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key) # Execution de la méthode qui gère les touches enfoncées

    def handle_keydown(self, key: int) -> None:
        """ Aiguille l'action d'une touche selon l'état actuel du jeu """

        if key == pygame.K_F11:  #Passage en plein écran (si on fait F11)
            try:
                pygame.display.toggle_fullscreen()
            except pygame.error:
                print("Plein écran non disponible")  #pour handle si pas possible de passer en plein écran sans faire crash le jeu
            return

        menu = self.model.current_menu()
        if menu is not None:  #Si on est dans un menu
            self.handle_menu_key(menu, key)
        elif self.model.state == c.GameState.RACING and key == pygame.K_ESCAPE:  #Pas de menu en course : Echap ouvre la pause
            self.model.change_state(c.GameState.PAUSE)
        elif self.model.state == c.GameState.RACING:
            for index, handler in enumerate(self.input_handlers):
                # Gestion touche pour utilisation item
                if key in handler.keybinds.get("use_item", []):
                    self.model.use_item(index, self.audio_handler)
                # Gestion touche pour klaxon
                elif key in handler.keybinds.get("klaxon", []):
                    sound_name = f'horn{index+1}'
                    self.audio_handler.play_sound(sound_name)
                # Gestion touche pour revenir au dernier point de passage
                elif key in handler.keybinds.get("respawn", []):
                    self.model.respawn(index)

        if self.model.state == c.GameState.LOADING:  #Un circuit vient d'être choisi
            self.render()  #On affiche l'écran de chargement avant de charger, sinon il n'apparaîtrait jamais
            self.model.start_race()

        if self.model.state == c.GameState.QUIT:  #Le menu a demandé à quitter : c'est le contrôleur qui arrête le jeu
            self.quit()

    def handle_menu_key(self, menu, key: int):
        """Mêmes touches pour tous les menus """
        if key in UP_KEYS:
            menu.move(-1)
        elif key in DOWN_KEYS:
            menu.move(1)
        elif key == pygame.K_RETURN:
            menu.select()  #Chaque menu fait sa propre action
        elif key == pygame.K_ESCAPE:
            menu.back()

    def update(self) -> None:
        """ Mise à jour de la logique du jeu et de la physique de la voiture """

        # Sécurité si le jeu n'est pas en cours de course
        if self.model.state != c.GameState.RACING:
            return

        for player, handler in zip(self.model.players, self.input_handlers):
            player_input = handler.get_inputs() # Récupération d'un dictionnaire comportant toutes les actions avec un booléen
            self.apply_input(player.car, player_input) # Application du dictionnaire des inputs sur l'instance de la voiture
        self.model.update(self.audio_handler) # Mise à jour du modèle

    def apply_input(self, car, player_input) -> None:
        """ Modification des paramètres internes de l'instance car avec les paramètres du dictionnaire player_input"""

        # on passe les inputs à la classe voiture qui gère ensuite la physique selon les inputs
        car.compute_new_metrics(player_input)

    def render(self) -> None:
        """ Affichage de l'état du modèle dans la fenêtre de jeu """

        self.view.draw(self.model)

    def quit(self) -> None:
        """ Méthode de sortie du jeu"""

        self.running = False # Permet de cesser la boucle de la méthode run
        pygame.quit() # Libération de l'espace mémoire alloué à pygame
        sys.exit() # Arrêt de l'interpréteur Python

    def music(self):
        self.audio_handler.update_music()
