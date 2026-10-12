# Documentation développeur

Ce document décrit l'état **actuel** du code.

## Lancer le projet

Depuis la racine du dépôt :

```bash
python main.py
```

Le point d'entrée `main.py` initialise pygame, crée `GameController`, puis lance la boucle de jeu.

## Architecture MVC actuellement implémentée

- **Modèle** (`/home/runner/work/Mario-Kart-Python/Mario-Kart-Python/model`)
  - `game_model.py` : état global (`MENU` / `RACING`), chargement du circuit, création de la voiture.
  - `car.py` : physique minimale (accélération, mise à jour de position verticale).
  - `circuit.py` et `road_tile.py` : grille et rendu des tuiles de route.
- **Vue** (`/home/runner/work/Mario-Kart-Python/Mario-Kart-Python/view`)
  - `game_view.py` : rendu du menu, du circuit et de la voiture.
- **Contrôleur** (`/home/runner/work/Mario-Kart-Python/Mario-Kart-Python/controller`)
  - `game_controller.py` : boucle principale, événements clavier, transition menu/course.
  - `input_handler.py` : mapping des touches actives pendant la course.

## Flux runtime

1. L'application démarre dans l'état `GameState.MENU`.
2. `Entrée` charge le circuit (`GameModel.load_circuit`) et passe en `GameState.RACING`.
3. En course, `InputHandler.get_inputs` lit le clavier et expose seulement l'action `accelerate`.
4. `GameController.apply_input` applique l'accélération à `model.car`.
5. `GameModel.update` avance ensuite la voiture via `Car.update_position`.

## Vérification locale

Le dépôt inclut `pytest` dans `requirements.txt`, mais aucun test n'est encore présent.
La commande de vérification exécutable actuellement est :

```bash
python -m pytest
```

(résultat attendu à ce stade : `collected 0 items`)
