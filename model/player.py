from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.car import Car

class Player:
    """Joueur : son numéro, son nom, sa voiture et son objet."""

    def __init__(self, index: int, car: Car):
        """Crée le joueur numéro index (0 ou 1) avec sa voiture"""
        self.index = index
        self.name = f"Joueur {index + 1}"
        self.car = car
        self.item = None #objet possédé
