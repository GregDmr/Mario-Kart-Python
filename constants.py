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

#Modèle transitoire du pneu (déformation du patch de contact)
RELAX_LENGTH = 0.3 #m, distance roulée pour atteindre 63% de la force
RELAX_SPEED_MIN = 1.0 #m/s, sous cette vitesse la déformation se dissipe quand meme lentement
MAX_SLIP = 0.2 #glissement max stocké dans le patch (pic de Pacejka vers 0.15)
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
WHEEL_LENGTH = [0.6] #m, taille de la roue vue de dessus, dans le sens de roulage
WHEEL_WIDTH = [0.3] #m
CAR_IZZ = [800] #KG * m²