import pygame


class InputHandler:
    """ Gestionnaire des entrées clavier pour traduire les touches physiques en actions """
    def __init__(self, keybinds: dict[str, list[int]]):
        """ Constructeur de la classe InputHandler """
        self.keybinds = keybinds #référence vers les touches du joueur dans le modèle

    def get_inputs(self) -> dict:
        """ Récupère l'état instantané du clavier et retourne un dictionnaire d'actions """

        # Récupération de l'état de toutes les touches du clavier 
        keys = pygame.key.get_pressed()

        # Initialise toutes les actions du mapping avec False par défaut
        p = {action: False for action in self.keybinds}

        # Parcourt le mapping pour vérifier si les touches associées sont enfoncées
        for action, action_keys in self.keybinds.items():
            for key in action_keys:
                # Si la touche est appuyé on passe l'action à True
                if keys[key]:
                    p[action] = True

        # On retourne le dictionnaire des actions
        return p

    def is_item_key(self, key: int) -> bool:
        """ Indique si la touche sert à utiliser un objet """
        return key in self.keybinds["use_item"]
