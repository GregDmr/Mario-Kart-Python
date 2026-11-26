from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.car import Car
    from model.circuit import Circuit

class Player:
    """Joueur : son numéro, son nom, sa voiture et son objet."""

    def __init__(self, index: int, car: Car):
        """Crée le joueur numéro index (0 ou 1) avec sa voiture"""
        self.index = index
        self.name = f"Joueur {index + 1}"
        self.car = car
        self.item = None #objet possédé
        self.next_checkpoint = 0  #indice du prochain point de passage à franchir
        self.laps = 0  #tours terminés
        self.respawn_point = (car.x, car.y, car.angle)  #dernier point franchi (x, y, angle), le départ au début

    def use_item(self, audio_controller=None):
        """ Utilisation de l'objet du joueur """
        # Vérification si le joueur a un objet
        if self.item is not None:
            # Utilisation de la méthode use de l'item du joueur
            drop_item = self.item.use(self, audio_controller)
            # On vide l'inventaire du joueur
            self.item = None
            # On retourne l'objet drop pour le game_model
            return drop_item

    def respawn(self) -> None:
        """Ramène la voiture au dernier point de passage franchi, à l'arrêt"""
        x, y, angle = self.respawn_point
        self.car.reset(x, y, angle)

    def update_progress(self, circuit: Circuit) -> None:
        """Valide le prochain point de passage, ou la ligne d'arrivée une fois tous les points franchis"""
        if self.next_checkpoint < len(circuit.checkpoints):
            checkpoint = circuit.checkpoints[self.next_checkpoint]
            if checkpoint.contains(self.car.x, self.car.y):
                self.next_checkpoint += 1
                self.respawn_point = checkpoint.respawn_position()
        elif circuit.finish_line.contains(self.car.x, self.car.y):
            self.laps += 1
            self.next_checkpoint = 0
            self.respawn_point = circuit.finish_line.respawn_position()
