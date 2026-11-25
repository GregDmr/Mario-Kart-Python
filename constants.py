import pygame
from pathlib import Path

FPS = 60

TILE_SIZE = 1
GRID_COLS = 120*12
GRID_ROWS = 68*12

GRAVITY = 9.81 #m/s²

PIXEL_PER_METER = 20#super important a définir plus tard, permet de lier la physique du modèle car avec le rendu 

WINDOW_WIDTH = TILE_SIZE * GRID_COLS
WINDOW_HEIGHT = TILE_SIZE * GRID_ROWS

#Propriétés des ROAD_TILES

FRICTION_COEFFS = [1.8 ,0.75,0,0.4] #route, herbe, mur, glace

#Coefficients de la Magic Tire Equation
PACEJKA_B_LONG = 10
PACEJKA_C_LONG = 1.4
PACEJKA_E_LONG = -1
PACEJKA_B_LAT = 10
PACEJKA_C_LAT = 1.3 #palier à environ 0.89 du pic
PACEJKA_E_LAT = -2.2 #place le pic à un glissement d'environ 0.15, comme en longitudinal

#Modèle transitoire du pneu (déformation du patch de contact)
RELAX_LENGTH = 0.3 #m, distance roulée pour atteindre 63% de la force
RELAX_SPEED_MIN = 1.0 #m/s, sous cette vitesse la déformation se dissipe quand meme lentement
MAX_SLIP = 0.2 #glissement max stocké dans le patch (pic de Pacejka vers 0.15)
class GameState:
    MENU = "menu"
    TRACK_SELECT = "track_select"
    LOADING = "loading"
    RACING = "racing"
    PAUSE = "pause"
    QUIT = "quit"


# --- Couleurs UI ---
COLOR_BG = (15, 15, 25)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (255, 200, 0)
COLOR_PANEL = (30, 30, 50)
COLOR_PANEL_BORDER = (60, 60, 100)
COLOR_HINT = (150, 150, 170)
COLOR_HUD = (255, 0, 0)

#Charactéristiques des voitures : [voiture test jaune, DK, WL, YO]
#voiture test = petite sportive, karts = karts haut de gamme (rapport poids/puissance élevé, CG bas, empattement court)
RWD = [1,1,1,1] #bool, true si propulsion, false si traction
STEERING_VELOCITY = [0.1,0.12,0.14,0.16] #Vitesse de rotation du volant, valeur sans unité
STEERING_RANGE = [0.6,0.5,0.5,0.5] #angle max de rotation des roues , RADIAN
STEERING_SPEED_REF = 12 #vitesse (m/s) à laquelle le braquage est divisé par 2
WHEEL_BASE = [2.8,1.0,1.0,1.0] #entraxe des roues longitudinal, METRE
WHEEL_TRACK = [1.65,1.15,1.15,1.15] #entraxe des roues latéral, METRE
MAX_ENGINE_TORQUE = [250,125,117,106] #couple max du moteur , N * m
MAX_BRAKING_TORQUE = [950,275,255,230]
BRAKE_BIAS_FRONT = 0.8 #part du freinage sur l'essieu avant (0.5 = répartition égale), élevé pour que l'arrière ne bloque pas en premier
CENTER_GRAVITY_Z = [0.45,0.2,0.2,0.2] #hauteur du CG en m
CENTER_GRAVITY_X = [0.05,-0.1,-0.1,-0.12] #position longitudinale du CG a partir du centre geométrique de la voiture (pos ou neg)
MASS = [900,195,180,165]  #masse en kg (pilote compris pour les karts)
CAR_WIDTH = [2,1.5,1.5,1.5] #m
CAR_HEIGHT = [4.7,2,2,2]#m
WHEEL_LENGTH = [0.65,0.38,0.38,0.38] #m, taille de la roue vue de dessus, dans le sens de roulage
WHEEL_WIDTH = [0.25,0.25,0.25,0.25] #m
TIRE_RADIUS = [0.3,0.15,0.15,0.15] #m, rayon de roulement (sert au glissement et au régime moteur)
WHEEL_INERTIA = [1.2,0.3,0.3,0.3] #KG * m², inertie d'une roue en rotation
FINAL_DRIVE = [4,2,2,2] #rapport de transmission moteur -> roues, proportionnel au rayon pour garder la même vitesse max et la même force aux roues
CAR_IZZ = [1100,72,68,60] #KG * m²
CAR_SPRITE = ["01_yellow_test.png", "02_DK.png", "03_WL.png", "04_YO.png"]
CAR_SPRITES_DIRECTORY = "assets/sprites/cars"

#Touches par défaut de chaque joueur (action -> touches)
DEFAULT_KEYBINDS = [
    {"accelerate": [pygame.K_z, pygame.K_w], 
     "decelerate": [pygame.K_s],
     "turn_left": [pygame.K_q, pygame.K_a], 
     "turn_right": [pygame.K_d], 
     "use_item": [pygame.K_SPACE],
     "klaxon": [pygame.K_LSHIFT]},
    
    {"accelerate": [pygame.K_UP], 
     "decelerate": [pygame.K_DOWN],
     "turn_left": [pygame.K_LEFT],
     "turn_right": [pygame.K_RIGHT], 
     "use_item": [pygame.K_RETURN],
     "klaxon": [pygame.K_RSHIFT]}
]

# -- PATH --
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Dossiers spécifiques
PATH_ITEMS = ASSETS_DIR / "items"
PATH_TRACKS = ASSETS_DIR / "tracks"

# Sprites des items
SPRITE_ITEMBOX = PATH_ITEMS / "sprite_itembox.webp"
SPRITE_FAKE_ITEMBOX = PATH_ITEMS / "sprite_fake_itembox.webp"
SPRITE_BANANA = PATH_ITEMS / "sprite_banane.webp"
SPRITE_MUSHROOM = PATH_ITEMS / "sprite_mushroom.webp"
SPRITE_GREEN_SHELL = PATH_ITEMS / "sprite_green_shell.webp"
SPRITE_BLUE_SHELL = PATH_ITEMS / "sprite_blue_shell.webp"
SPRITE_STAR = PATH_ITEMS / "sprite_star.webp"
SPRITE_BOBOMB = PATH_ITEMS / "sprite_bobomb.webp"