import os
import json
from abc import ABC, abstractmethod
from constants import GameState, PATH_TRACKS



def texture_path(track_path: str):
    """Image affichée d'un circuit : sa texture si elle existe, sinon la carte elle-même"""
    texture = os.path.splitext(track_path)[0] + "_texture.png"  #"xx_nom.png" devient "xx_nom_texture.png"
    if os.path.exists(texture):
        return texture
    return track_path

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
    """Choix du circuit parmi les cartes disponibles"""

    title = "Choix du circuit"

    def __init__(self, game_model):
        # On liste uniquement les fichiers JSON 
        json_names = sorted(n for n in os.listdir(PATH_TRACKS) if n.lower().endswith(".json"))
        self.tracks = [os.path.join(PATH_TRACKS, n) for n in json_names]

        # On extrait le track_name de chaque JSON pour l'affichage dans le menu
        display_names = []
        for path in self.tracks:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("track_name", "Circuit").replace("_", " ")
                display_names.append(name)

        super().__init__(game_model, display_names)

    def select(self):
        # Transmet le chemin du JSON sélectionné au GameModel
        self.game_model.prepare_race(self.tracks[self.selected])

    def back(self):
        self.game_model.change_state(GameState.MENU)

    def preview_path(self):
        """Retrouve l'image PNG de texture associée au JSON sélectionné"""

        json_path = self.tracks[self.selected]
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # On reconstruit le chemin de l'image à partir du track_name du JSON
        track_name = data.get("track_name")
        png_path = os.path.join(PATH_TRACKS, f"{track_name}.png")

        return png_path



class PauseMenu(Menu):
    """Pause : reprendre la course, la recommencer ou revenir au menu principal"""

    title = "Pause"

    def __init__(self, game_model):
        super().__init__(game_model, ["Reprendre", "Recommencer", "Menu principal"])

    def select(self):
        if self.selected == 0:  #Option "Reprendre" : la course repart là où elle était
            self.game_model.change_state(GameState.RACING)
        elif self.selected == 1:  #Option "Recommencer" : mêmes voitures, même circuit
            self.game_model.restart_race()
        else:  #Option "Menu principal" : la course est abandonnée
            self.game_model.change_state(GameState.MENU)

    def back(self):
        self.game_model.change_state(GameState.RACING)  #Echap en pause reprend la course
