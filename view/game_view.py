import os
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_HINT,
    GameState
)
from model.game_model import GameModel
from model.menu import Menu, track_name

MAX_VISIBLE_OPTIONS = 6  #Au-delà, la liste défile

HINTS = {  #Rappel des touches propre à chaque écran
    GameState.MENU: "↑ ↓ : choisir    Entrée : valider    Echap : quitter",
    GameState.TRACK_SELECT: "↑ ↓ : choisir    Entrée : lancer la course    Echap : retour",
    GameState.PAUSE: "↑ ↓ : choisir    Entrée : valider    Echap : reprendre",
}


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)  #Police du titre des menus
        self.hint_font = pygame.font.SysFont("Arial", 18)  #Police du rappel des touches
        self.name_font = pygame.font.SysFont("Arial", 36, bold=True)  #Police du nom sous l'aperçu
        self.previews: dict[str, pygame.Surface] = {}  #Miniatures déjà calculées, pour ne pas recharger l'image à chaque frame

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state in (GameState.RACING, GameState.PAUSE):  #En pause, la course reste affichée, figée
            self._draw_racing(model)
        menu = model.current_menu()
        if model.state == GameState.PAUSE:
            self._draw_veil()
            self._draw_menu(menu, panel=True)
        elif menu is not None:  #Si on est dans un menu (peu importe lequel)
            self._draw_menu(menu)
        elif model.state == GameState.LOADING:
            self._draw_loading(model.pending_track)

        if model.state in HINTS:
            self._draw_hint(HINTS[model.state])
        pygame.display.flip()

    def _draw_menu(self, menu: Menu, panel: bool = False):
        """Dessine n'importe quel menu : titre, options, aperçu éventuel et rappel des touches"""
        preview = menu.preview_path()
        cx = WINDOW_WIDTH * 3 // 10 if preview else WINDOW_WIDTH // 2  #Avec un aperçu, la liste passe à gauche
        title_y, first_y = 140, 280

        if panel:  #Menu dans un encadré au centre de l'écran (pause)
            box = pygame.Rect(0, 0, 420, 320)
            box.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.rect(self.screen, COLOR_BG, box, border_radius=12)
            pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, box, 2, border_radius=12)
            title_y, first_y = box.top + 70, box.top + 170

        title = self.title_font.render(menu.title, True, COLOR_ACCENT)  #Le titre dépend du menu (chaque sous-classe a le sien)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, title_y)))

        first = max(0, min(menu.selected - MAX_VISIBLE_OPTIONS // 2, len(menu.options) - MAX_VISIBLE_OPTIONS))  #Première option affichée : la liste défile pour garder la sélection à l'écran
        visible = menu.options[first:first + MAX_VISIBLE_OPTIONS]
        for i, label in enumerate(visible, start=first):  #enumerate donne l'indice i en plus du texte, pour savoir si c'est l'option sélectionnée
            rect = pygame.Rect(0, 0, 320, 56)
            rect.center = (cx, first_y + (i - first) * 72)
            is_selected = i == menu.selected
            pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=8)
            border = COLOR_ACCENT if is_selected else COLOR_PANEL_BORDER
            pygame.draw.rect(self.screen, border, rect, 3 if is_selected else 2, border_radius=8)  #Avec une épaisseur, draw.rect ne trace que le contour
            text = self.font.render(label, True, COLOR_ACCENT if is_selected else COLOR_TEXT)
            self.screen.blit(text, text.get_rect(center=rect.center))

        if first > 0:  #Flèches : il reste des options cachées au-dessus ou en dessous
            pygame.draw.polygon(self.screen, COLOR_HINT, [(cx, first_y - 58), (cx - 14, first_y - 42), (cx + 14, first_y - 42)])
        if first + MAX_VISIBLE_OPTIONS < len(menu.options):
            pygame.draw.polygon(self.screen, COLOR_HINT, [(cx, first_y + 418), (cx - 14, first_y + 402), (cx + 14, first_y + 402)])

        if preview:
            self._draw_preview_panel(preview, menu.options[menu.selected])

    def _draw_hint(self, text: str):
        """Rappel des touches en bas de l'écran"""
        hint = self.hint_font.render(text, True, COLOR_HINT)
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))

    def _draw_loading(self, track_path: str):
        """Ecran affiché pendant le chargement du circuit"""
        text = self.title_font.render("Chargement...", True, COLOR_ACCENT)
        self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))
        name = self.name_font.render(track_name(os.path.basename(track_path)), True, COLOR_TEXT)  #basename : on garde "01_test_track.png" sans le dossier
        self.screen.blit(name, name.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)))

    def _draw_veil(self):
        """Voile sombre semi-transparent sur tout l'écran"""
        veil = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  #SRCALPHA : surface qui gère la transparence
        veil.fill((0, 0, 0, 160))  #4e valeur : opacité, de 0 (invisible) à 255 (opaque)
        self.screen.blit(veil, (0, 0))

    def _draw_preview_panel(self, image_path: str, name: str):
        """Encadré à droite : miniature de l'image et nom de l'option sélectionnée"""
        panel = pygame.Rect(0, 0, 620, 440)
        panel.center = (WINDOW_WIDTH * 2 // 3, 450)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, panel, 2, border_radius=12)

        if image_path not in self.previews:  #Chargement et réduction une seule fois par image
            image = pygame.image.load(image_path).convert_alpha()
            self.previews[image_path] = pygame.transform.smoothscale(image, (560, 317))  #Même proportion que la fenêtre
        preview = self.previews[image_path]
        rect = preview.get_rect(midtop=(panel.centerx, panel.top + 30))
        self.screen.blit(preview, rect)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, rect.inflate(6, 6), 3)

        name_text = self.name_font.render(name, True, COLOR_TEXT)
        self.screen.blit(name_text, name_text.get_rect(center=(panel.centerx, rect.bottom + 45)))

    def _draw_racing(self, model: GameModel) -> None:

        self.screen.blit(model.circuit_texture_render,(0,0))
        
        if model.circuit is None:
            return
        #affichage des tire marks, avant la voiture pour qu'elles soient dessous
        for tire_mark in model.car.tire_mark_list:
            sprite, rect = tire_mark.mark_sprite()
            alpha = max(0, 255 * tire_mark.lifespan // tire_mark.lifespan_init) #255 = opaque, 0 = invisible
            sprite.set_alpha(alpha)
            self.screen.blit(sprite, rect)

        surf, rect = model.car.get_rotated_sprite() # a faire pour chaque voiture eventuellement
        self.screen.blit(surf, rect)
        surf_texte = model.car.debug_variables(self.font)
        self.screen.blit(surf_texte, (10,10))

        # Affichage des items sur la piste (cubes, bananes, etc)
        for item in model.items:
            item.draw(self.screen)

        # Affichage des coordonnées de la souris en temps réel (Debug)
        mx, my = pygame.mouse.get_pos()
        mouse_surf = self.font.render(f"Souris: ({mx}, {my})", True, (255, 255, 0))
        self.screen.blit(mouse_surf, (WINDOW_WIDTH - 200, 10))
        
        
