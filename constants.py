FPS = 60

TILE_SIZE = 1
GRID_COLS = 120*12
GRID_ROWS = 68*12

PIXEL_PER_METER = 10 #super important a définir plus tard, permet de lier la physique du modèle car avec le rendu 

WINDOW_WIDTH = TILE_SIZE * GRID_COLS
WINDOW_HEIGHT = TILE_SIZE * GRID_ROWS

MAX_SPEED = 4
MAX_REVERSE_SPEED = 2
CAR_ACCELERATION = 0.05
CAR_BRAKE = 0.1
CAR_REVERSE = 0.02
CAR_FRICTION = 0.01

CAR_WIDTH = 30
CAR_HEIGHT = 50


class GameState:
    MENU = "menu"
    RACING = "racing"


# --- Couleurs UI ---
COLOR_BG = (15, 15, 25)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (255, 200, 0)
COLOR_PANEL = (30, 30, 50)
COLOR_PANEL_BORDER = (60, 60, 100)

#Charactéristiques des voitures, placeholder pour le moment

STEERING_VELOCITY = [0.1,0.15] #Vitesse de rotation du volant, valeur sans unité
STEERING_RANGE = [0.8,1.1] #angle max de rotation des roues , RADIAN
WHEEL_BASE = [] #entraxe des roues longitudinal, METRE
WHEEL_TRACK = [] #entraxe des roues latéral, METRE
MAX_ENGINE_TORQUE = [20] #couple max du moteur , N * m
CENTER_GRAVITY_Z = [0.3] #hauteur du CG en m
CENTER_GRAVITY_X = [0.8] #position longitudinale du CG a partir des roues avant, en m
MASS = [1200]  #masse en kg