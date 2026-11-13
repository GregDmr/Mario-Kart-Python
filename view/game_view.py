import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_HINT,
    GameState
)
from model.game_model import GameModel
from model.menu import Menu


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)  #Police du titre des menus
        self.hint_font = pygame.font.SysFont("Arial", 18)  #Police du rappel des touches

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.RACING:
            self._draw_racing(model)
        menu = model.current_menu()
        if menu is not None:  #Si on est dans un menu (peu importe lequel)
            self._draw_menu(menu)
        pygame.display.flip()

    def _draw_menu(self, menu: Menu):
        """Dessine n'importe quel menu : titre, options et rappel des touches"""
        title = self.title_font.render(menu.title, True, COLOR_ACCENT)  #Le titre dépend du menu (chaque sous-classe a le sien)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 140)))  #Centré horizontalement, en haut de l'écran

        for i, label in enumerate(menu.options):  #enumerate donne l'indice i en plus du texte, pour savoir si c'est l'option sélectionnée
            rect = pygame.Rect(0, 0, 320, 56)  #Taille du bouton, la position est donnée juste après
            rect.center = (WINDOW_WIDTH // 2, 340 + i * 80)  #Chaque bouton est 80 px sous le précédent
            is_selected = i == menu.selected
            pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=8)  #Fond du bouton
            border = COLOR_ACCENT if is_selected else COLOR_PANEL_BORDER  #Bordure colorée seulement sur l'option sélectionnée
            pygame.draw.rect(self.screen, border, rect, 3 if is_selected else 2, border_radius=8)  #Avec une épaisseur, draw.rect ne trace que le contour
            text = self.font.render(label, True, COLOR_ACCENT if is_selected else COLOR_TEXT)
            self.screen.blit(text, text.get_rect(center=rect.center))  #Texte centré dans son bouton

        hint = self.hint_font.render("↑ ↓ : choisir    Entrée : valider    Echap : retour", True, COLOR_HINT)  #Rappel des touches
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))  #En bas de l'écran

    def _draw_racing(self, model: GameModel) -> None:

        self.screen.blit(model.circuit_texture_render,(0,0))
        
        if model.circuit is None:
            return
        surf, rect = model.car.get_rotated_sprite() # a faire pour chaque voiture eventuellement
        self.screen.blit(surf, rect)
        surf_texte = model.car.debug_variables(self.font)
        self.screen.blit(surf_texte, (10,10))
        
