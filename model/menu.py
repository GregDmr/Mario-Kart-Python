import os
from abc import ABC, abstractmethod
from constants import GameState

TRACKS_DIRECTORY = "assets/tracks"


def texture_path(track_path: str):
    """Image affichée d'un circuit : sa texture si elle existe, sinon la carte elle-même"""
    texture = os.path.splitext(track_path)[0] + "_texture.png"  #"xx_nom.png" devient "xx_nom_texture.png"
    if os.path.exists(texture):
        return texture
    return track_path


def track_name(file_name: str):
    """Nom affiché d'un circuit : "01_test_track.png" donne "Test track" """
    name = os.path.splitext(file_name)[0]
    number, _, rest = name.partition("_")
    if number.isdigit() and rest:  #On retire le numéro d'ordre s'il y en a un
        name = rest
    return name.replace("_", " ").capitalize()


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

    def preview_path(self):
        """Image d'aperçu de l'option sélectionnée, aucune par défaut"""
        return None  #Seul TrackMenu la redéfinit


class MainMenu(Menu):
    """Menu principal : jouer ou quitter (penser à rajouter une option keybinds si on veut rajouter la possibilité de choisir ses touches) """

    title = "Jeu de course 2D"

    def __init__(self, game_model):
        super().__init__(game_model, ["Jouer", "Quitter"])  #Appelle le constructeur de Menu avec les options de ce menu

    def select(self):
        if self.selected == 0:  #Option "Jouer"
            self.game_model.change_state(GameState.TRACK_SELECT)
        else:  #Option "Quitter" : le modèle ne ferme pas le jeu lui-même, il passe en QUIT et le contrôleur s'en charge
            self.game_model.change_state(GameState.QUIT)

    def back(self):
        self.game_model.change_state(GameState.QUIT)  #Echap dans le menu principal quitte le jeu


class TrackMenu(Menu):
    """Choix du circuit parmi les cartes du dossier des circuits"""

    title = "Choix du circuit"

    def __init__(self, game_model):
        names = sorted(n for n in os.listdir(TRACKS_DIRECTORY)
                       if n.lower().endswith(".png") and not n.lower().endswith("_texture.png"))  #On garde les cartes, pas les textures
        self.tracks = [os.path.join(TRACKS_DIRECTORY, n) for n in names]
        super().__init__(game_model, [track_name(n) for n in names])

    def select(self):
        self.game_model.prepare_race(self.tracks[self.selected])  #La course est chargée à l'écran suivant

    def back(self):
        self.game_model.change_state(GameState.MENU)

    def preview_path(self):
        return texture_path(self.tracks[self.selected])


class PauseMenu(Menu):
    """Pause : reprendre la course ou revenir au menu principal"""

    title = "Pause"

    def __init__(self, game_model):
        super().__init__(game_model, ["Reprendre", "Menu principal"])

    def select(self):
        if self.selected == 0:  #Option "Reprendre" : la course repart là où elle était
            self.game_model.change_state(GameState.RACING)
        else:  #Option "Menu principal" : la course est abandonnée
            self.game_model.change_state(GameState.MENU)

    def back(self):
        self.game_model.change_state(GameState.RACING)  #Echap en pause reprend la course
