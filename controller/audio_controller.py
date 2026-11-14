import pygame
import os
from constants import GameState

class AudioController :

    def __init__(self, gameModel): #On passe le gameModel pour avoiracces au status actuel du jeu
        self.current_track = None
        self.acces_status = gameModel

        # Flags pour gérer la musique et les bruitages
        self.music_enabled = True 
        self.sfx_enabled = True        

        # Gestion des bruitages
        self.sounds = {} 
        self.load_all_sounds("assets/sounds")

    def load_all_sounds(self, folder_path: str) -> None:
        """ Fonction pour parcourir tout le dossier des sons et les charger dans le dictionnaire. """
        for filename in os.listdir(folder_path):
            sound_name = os.path.splitext(filename)[0]
            file_path = os.path.join(folder_path, filename)
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(0.8) # Réglage du volume des sons
            self.sounds[sound_name] = sound

    def play_sound(self, sound_name: str) -> None:
        " Joue le nom du son passé en paramètres. "

        # Si le s
        if not self.sfx_enabled:
            return 
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        # Pour débug
        else:
            print("Son non trouvé")

    def update_music(self):

        if not self.music_enabled:
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
