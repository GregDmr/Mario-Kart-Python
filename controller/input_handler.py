import pygame

# Dictionnaire de correspondance touche action
MAPPING = {
    pygame.K_UP:     "accelerate",
}


class InputHandler:
    """ Gestionnaire des entrées clavier pour traduire les touches physiques en actions """
    def __init__(self):
        """ Constructeur de la classe InputHandler """
        self.mapping = MAPPING

    def get_inputs(self) -> dict:
        """ Récupère l'état instantané du clavier et retourne un dictionnaire d'actions """

        # Récupération de l'état de toutes les touches du clavier 
        keys = pygame.key.get_pressed()

        # Initialise toutes les actions du mapping avec False par défaut
        p = {action: False for action in self.mapping.values()}

        # Parcourt le mapping pour vérifier si les touches associées sont enfoncées
        for key, action in self.mapping.items():
            # Si la touche est appuyé on passe l'action à True
            if keys[key]:
                p[action] = True

        # On retourne le dictionnaire des actions
        return p
