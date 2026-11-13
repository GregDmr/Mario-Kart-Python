from abc import ABC, abstractmethod
from constants import GameState


class Menu(ABC):
    """Classe pour un menu générique"""

    title: str = ""

    def __init__(self, game_model, options: list[str]):
        """Crée le menu à partir du modèle et de ses options"""
        self.game_model = game_model  #Modèle sur lequel agit le menu (pour changer d'état, lancer la course...)
        self.options = options  #Textes affichés sur les boutons
        self.selected = 0  #On commence dans la liste de choix au premier, donc 0 de la liste

    def move(self, delta: int):
        """Déplacement du curseur dans la liste d'options du menu"""
        self.selected = (self.selected + delta) % len(self.options)  #On fait ça pour gérer le bouclage : quand on arrive à la dernière option, continuer refait passer sur la première

    @abstractmethod
    def select(self):
        """ Action de la touche Entrée """

    @abstractmethod
    def back(self):
        """Action de la touche Echap """


class MainMenu(Menu):
    """Menu principal : jouer ou quitter (penser à rajouter une option keybinds si on veut rajouter la possibilité de choisir ses touches) """

    title = "Jeu de course 2D"

    def __init__(self, game_model):
        super().__init__(game_model, ["Jouer", "Quitter"])  #Appelle le constructeur de Menu avec les options de ce menu

    def select(self):
        if self.selected == 0:  #Option "Jouer"
            self.game_model.start_race()
        else:  #Option "Quitter" : le modèle ne ferme pas le jeu lui-même, il passe en QUIT et le contrôleur s'en charge
            self.game_model.change_state(GameState.QUIT)

    def back(self):
        self.game_model.change_state(GameState.QUIT)  #Echap dans le menu principal quitte le jeu
