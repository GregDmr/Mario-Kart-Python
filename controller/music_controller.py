import pygame
import os 
from constants import GameState

class MusicController :

    def __init__(self, gameModel): #On passe le gameModel pour avoiracces au status actuel du jeu
        self.current_track = None
        self.acces_status = gameModel

    def update(self):
        current_status = self.acces_status.state
        if self.current_track != "menu" and current_status == GameState.MENU:
            self.load_music("menu_music.mp3")
            pygame.mixer.music.play(-1)
            self.current_track = "menu"
        if self.current_track != "racing" and current_status == GameState.RACING:
            self.load_music("racing_music.mp3")
            pygame.mixer.music.play(-1)
            self.current_track = "racing"

    def load_music(self, music_to_load : str):
        path = os.path.join("assets/music", music_to_load)
        pygame.mixer.music.load(path)
