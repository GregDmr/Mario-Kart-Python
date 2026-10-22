"""Conversion d'une image de circuit en matrice d'ID de tuiles.

La matrice est générée à chaque lancement du jeu, à partir de l'image choisie.
"""
import os
import pygame
from constants import GRID_COLS, GRID_ROWS, TILE_SIZE


def convert_track(chosen_track_path : str) -> list[list[int]]:
    """Convertit une image de circuit en matrice d'ID de tuiles.

    L'image est redimensionnée à la taille de la fenêtre (GRID_COLS * TILE_SIZE
    par GRID_ROWS * TILE_SIZE). Pour chaque tuile, la couleur moyenne (r, g, b)
    est comparée aux couleurs de référence par somme des erreurs au carré, et
    l'ID de la référence la plus proche est retenu.

    Args:
        chosen_track_path: chemin de l'image du circuit (PNG 24 ou 32 bits).

    Returns:
        Matrice de GRID_ROWS lignes et GRID_COLS colonnes, accessible par
        matrix[row][col]. IDs : 0 = route, 1 = herbe, 2 = mur, 3 = eau.
    """
    image = pygame.image.load(chosen_track_path) #doit etre 24 bits ou plus
    resized = pygame.transform.smoothscale(image, (GRID_COLS * TILE_SIZE, GRID_ROWS * TILE_SIZE))
    references = [(48, 48, 48), (0, 255, 0), (127, 51, 0), (0,255,255)] #route, herbe, mur, eau
    matrix = []
    for row in range(GRID_ROWS):
        matrix_row = []
        for col in range(GRID_COLS):
            total_r = 0
            total_g = 0
            total_b = 0
            for y in range(row * TILE_SIZE, (row + 1) * TILE_SIZE):
                for x in range(col * TILE_SIZE, (col + 1) * TILE_SIZE):
                    r, g, b = resized.get_at((x, y))[:3]
                    total_r += r
                    total_g += g
                    total_b += b
            # moyenne r, g, b de la tuile
            nb_pixels = TILE_SIZE * TILE_SIZE
            average_color = [total_r // nb_pixels, total_g // nb_pixels, total_b // nb_pixels]
            # référence la plus proche de la moyenne (erreur au carré)
            best_match_id = 0
            error_tot = 0
            best_error = 999999999999
            for i in range(len(references)) :
                r,g,b = references[i]
                error_red = (r-average_color[0])**2
                error_green = (g-average_color[1])**2
                error_blue = (b-average_color[2])**2
                error_tot = error_blue + error_green + error_red
                if error_tot < best_error:
                    best_match_id = i
                    best_error = error_tot

            matrix_row.append(best_match_id)
        matrix.append(matrix_row)
    return matrix