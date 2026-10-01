# Jeu de course 2D (Python / pygame)

Jeu de course de voitures en 2D vu de dessus, pour **deux joueurs** sur le même clavier, développé avec [pygame](https://www.pygame.org/) dans le cadre d'un projet universitaire. Le code suit l'architecture **MVC** (Modèle – Vue – Contrôleur) : la logique du jeu, l'affichage et la gestion des entrées sont séparés dans trois dossiers distincts.

## Prérequis

- Python 3.x (développé et testé avec Python 3.13)
- git

## Installation

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/<utilisateur>/<repo>.git
   cd <repo>
   ```

2. Créer l'environnement virtuel :

   ```bash
   # Windows
   python -m venv .venv

   # macOS / Linux
   python3 -m venv .venv
   ```

3. Activer l'environnement virtuel :

   ```bash
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Windows (cmd)
   .venv\Scripts\activate.bat

   # macOS / Linux
   source .venv/bin/activate
   ```

4. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Lancement

```bash
python main.py
```

## Commandes du jeu

| Action                    | Joueur 1                | Joueur 2        |
|---------------------------|-------------------------|-----------------|
| Accélérer                 | `Z` (ou `W` en QWERTY)  | `↑`             |
| Freiner / marche arrière  | `S`                     | `↓`             |
| Tourner à gauche          | `Q` (ou `A` en QWERTY)  | `←`             |
| Tourner à droite          | `D`                     | `→`             |
| Action supplémentaire *(à préciser)* | `Espace`     | `Entrée`        |

## Structure du projet

```
.
├── main.py                  # Point d'entrée : initialise pygame et lance le contrôleur
├── constants.py             # Constantes partagées (fenêtre, FPS, tuiles, couleurs, états du jeu)
├── requirements.txt         # Dépendances Python (pygame, pytest)
├── model/                   # MODÈLE : état et logique du jeu, sans affichage
│   ├── car.py               #   Voiture (position, vitesse, rotation)
│   ├── circuit.py           #   Circuit (grille de tuiles)
│   ├── game_model.py        #   État global de la partie
│   └── road_tile.py         #   Tuile de route
├── view/                    # VUE : affichage pygame
│   └── game_view.py         #   Dessin du menu, du circuit et des voitures
└── controller/              # CONTRÔLEUR : boucle de jeu et entrées clavier
    ├── game_controller.py   #   Boucle principale, gestion des événements, mise à jour du modèle
    └── input_handler.py     #   Association touches clavier → actions
```

## Organisation du travail



## Répartition des tâches et planning


| Membre | Classes / fonctionnalités | Échéance |
|--------|---------------------------|----------|
|        |                           |          |
|        |                           |          |
|        |                           |          |

## Déclaration d'utilisation des outils d'IA


- [ ] Traduction / explication du sujet :
- [ ] Conception :
- [ ] Code :
- [ ] Débogage :
- [X] Commentaires et docstrings :
- [ ] Diagramme UML :

## Membres du groupe

- Louis PLOTTIER — 21202191
- Aurèle CAUCHETEUX — 21623770
- Grégoire DUMUR — 21224117
