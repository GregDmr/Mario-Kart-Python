import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    GameState
)
from model.game_model import GameModel


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.MENU:
            self._draw_menu(model)
        elif model.state == GameState.RACING:
            self._draw_racing(model)
        pygame.display.flip()

    def _draw_menu(self, model: GameModel) -> None:
        cx = WINDOW_WIDTH // 2

        title_surf = self.font.render(
            "Jeu de course 2D", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(cx, 160)))

        options = [("JOUER (Enter)", GameState.RACING),
                   ("QUITTER (Escape)", None)]
        for i, (label, _) in enumerate(options):
            y = 320 + i * 80
            rect = pygame.Rect(cx - 140, y - 25, 280, 50)
            pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_PANEL_BORDER,
                             rect, 2, border_radius=8)
            text_surf = self.font.render(
                label, True, COLOR_ACCENT if i == 0 else COLOR_TEXT)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_racing(self, model: GameModel) -> None:

        self.screen.blit(model.circuit_texture_render,(0,0))
        
        if model.circuit is None:
            return
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
        
        
