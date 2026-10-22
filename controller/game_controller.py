import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GameState
)
from model.game_model import GameModel
from view.game_view import GameView
from controller.input_handler import InputHandler
from controller.music_controller import MusicController

class GameController:

    def __init__(self):
        """ Constructeur de la classe GameController """

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Création de la fenêtre graphique
        self.clock = pygame.time.Clock() # Initialisation de l'horloge interne du jeu
        self.model = GameModel() # Instanciation de notre classe GameModel
        self.view = GameView(self.screen) # Connexion entre la partie graphique et la fenêtre de l'écran
        self.input_handler = InputHandler() # Initialisation du module pour gérer les entrées de  l'utilisateur
        self.music_handler = MusicController(self.model) #Il faut passer le modele pour que le controle de la musique sache l'etat du jeu.
        self.running = True # Booléen qui maintient la boucle du jeu active

    def run(self) -> None:
        """ Boucle principale du jeu (tourne en continu à chaque frame) """

        while self.running:
            self.handle_events() # Récupération des actions
            self.update() # Mise à jour de la logique ainsi que la position des éléments
            self.render() # Redessine tout à l'écran
            self.music()
            self.clock.tick(FPS) # Régulation de la vitesse d'affichage du jeu

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

        # Récupération de l'état actuel du jeu (menu, course, ...)
        state = self.model.state 

        # Si dans le menu principal
        if state == GameState.MENU:
            self.handle_menu_key(key) # Transmission de la touche enfoncée à la méthode handle_menu_key

    def handle_menu_key(self, key: int) -> None:
        """ Gestion des touches quand l'utilisateur est dans le menu principal """

        # Gestion de la touche Entrée
        if key == pygame.K_RETURN: #Ajouter une vérif si les voitures sont choisies ? 
            self.model.load_circuit() # Chargement des données du circuit
            self.model.state = GameState.RACING # PAssa ge de l'état du jeu de MENU à RACING

        # Gestion de la touche Echap
        elif key == pygame.K_ESCAPE:
            self.quit() # Execution de la méthode de sortie de jeu

    def update(self) -> None:
        """ Mise à jour de la logique du jeu et de la physique de la voiture """
        
        # Sécurité si le jeu n'est pas en cours de course
        if self.model.state != GameState.RACING:
            return

        p1_input = self.input_handler.get_inputs() # Récupération d'un dictionnaire comportant toutes les actions avec un booléen
        car = self.model.car # Récupération de l'instance de la voiture
        self.apply_input(car, p1_input) # Application du dictionnaire des inputs sur l'instance de la voiture
        self.model.update() # Mise à jour du modèle

    def apply_input(self, car, player_input) -> None:
        """ Modification des paramètres internes de l'instance car avec les paramètres du dictionnaire player_input"""

        # Si le joueur accélère, on appelle la méthode d'accélération définie dans la classe Car
        if player_input['accelerate']:
            car.accelerate()

    def render(self) -> None:
        """ Affichage de l'état du modèle dans la fenêtre de jeu """

        self.view.draw(self.model)

    def quit(self) -> None:
        """ Méthode de sortie du jeu"""

        self.running = False # Permet de cesser la boucle de la méthode run
        pygame.quit() # Libération de l'espace mémoire alloué à pygame
        sys.exit() # Arrêt de l'interpréteur Python
    
    def music(self):
        self.music_handler.update()