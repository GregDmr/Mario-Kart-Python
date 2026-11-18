FPS = 60

TILE_SIZE = 1
GRID_COLS = 120*12
GRID_ROWS = 68*12

GRAVITY = 9.81 #m/s²

PIXEL_PER_METER = 10#super important a définir plus tard, permet de lier la physique du modèle car avec le rendu 

WINDOW_WIDTH = TILE_SIZE * GRID_COLS
WINDOW_HEIGHT = TILE_SIZE * GRID_ROWS

#Propriétés des ROAD_TILES

FRICTION_COEFFS = [1.1 ,0.75,0,0.4] #route, herbe, mur, glace

#Coefficients de la Magic Tire Equation
PACEJKA_B_LONG = 10
PACEJKA_C_LONG = 1.4
PACEJKA_E_LONG = -1
PACEJKA_B_LAT = 10
PACEJKA_C_LAT = 1.3 #palier à environ 0.89 du pic
PACEJKA_E_LAT = -2.2 #place le pic à un glissement d'environ 0.15, comme en longitudinal
class GameState:
    MENU = "menu"
    TRACK_SELECT = "track_select"
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

#Charactéristiques des voitures, placeholder pour le moment
RWD = [1,0] #bool, true si propulsion, false si traction
STEERING_VELOCITY = [0.1,0.15] #Vitesse de rotation du volant, valeur sans unité
STEERING_RANGE = [0.8,1.1] #angle max de rotation des roues , RADIAN
WHEEL_BASE = [4] #entraxe des roues longitudinal, METRE
WHEEL_TRACK = [1.9] #entraxe des roues latéral, METRE
MAX_ENGINE_TORQUE = [180] #couple max du moteur , N * m
CENTER_GRAVITY_Z = [0.3] #hauteur du CG en m
CENTER_GRAVITY_X = [0.2] #position longitudinale du CG a partir du centre geométrique de la voiture (pos ou neg)
MASS = [600]  #masse en kg
CAR_WIDTH = [2] #m
CAR_HEIGHT = [4.7]#m
CAR_IZZ = [1500] #KG * m²
