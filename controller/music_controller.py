import pygame
import os
from constants import GameState

class MusicController :

    def __init__(self, gameModel): #On passe le gameModel pour avoiracces au status actuel du jeu
        self.current_track = None
        self.acces_status = gameModel
        self.enabled = True        #attribut pour gérer le cas où la musique ne peut pas être jouée

    def update(self):

        if not self.enabled:
            return

        current_status = self.acces_status.state
        if self.current_track != "menu" and current_status == GameState.MENU:
            self.load_music("menu_music.mp3")
            self.current_track = "menu"
        if self.current_track != "racing" and current_status == GameState.RACING:
            self.load_music("racing_music.mp3")
            self.current_track = "racing"

    def load_music(self, music_to_load: str):
        path = os.path.join("assets/music", music_to_load)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        except pygame.error as error:
            print(f"Error loading music file {path}: {error}")
            self.enabled = False  #On désactive la musique si erreur (ça évite le plantage)
