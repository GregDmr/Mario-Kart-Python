import pygame
import math
import os
import constants as c
from constants import PIXEL_PER_METER as ppm
from model.tire import Tire
from tools.degree_trig import sind, cosd
from model.circuit import Circuit
class Car:

    def __init__(self, circuit :Circuit, start_col: int, start_row: int, chosen_car : int =0):
        """ Initialise une voiture à partir de sa position sur la grille """
        #circuit a passer au pneu
        self.circuit = circuit
        #Attributs
        self.mass = c.MASS[chosen_car]
        self.wheelbase = c.WHEEL_BASE[chosen_car]
        self.wheeltrack = c.WHEEL_TRACK[chosen_car]
        self.center_grav_x = c.CENTER_GRAVITY_X[chosen_car]
        self.center_grav_z = c.CENTER_GRAVITY_Z[chosen_car]
        self.car_height = c.CAR_HEIGHT[chosen_car]
        self.car_width = c.CAR_WIDTH[chosen_car]
        self.steering_velocity = c.STEERING_VELOCITY[chosen_car]
        self.steering_range = c.STEERING_RANGE[chosen_car]
        self.max_torque = c.MAX_ENGINE_TORQUE[chosen_car]
        
        self.braking_torque = 300 #attention meme ordre de grandeur que engine torque (plus grand car freinage, mais le calcul pour la force est le meme)
        self.izz = c.CAR_IZZ[chosen_car]
        propulsion = c.RWD[chosen_car]
        self.final_drive = 4
        self.engine_speed_max = 750 #les deux valeurs a equilibrer en essais.
        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * c.TILE_SIZE + c.TILE_SIZE // 2
        self.y = start_row * c.TILE_SIZE + c.TILE_SIZE // 2

        # Initialisation vitesse et angle
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.omegad :float = 0.0
        self.angle: float = 0.0
        self.steering_multiplier : float = 0.0 #entre -1 et 1
        self.steering_angle : float = 0.0 #radians
        self.torque_multiplier : float = 0.0 #entre -1 et 1
        self.desired_torque : float = 0.0 #N.m
        self.angle : float =0.0
        # Génération du sprite visuel de base 
        self.sprite = self.build_sprite(chosen_car)

        #Pneus
        front_offset = self.wheelbase/2-self.center_grav_x
        rear_offset = (self.wheelbase/2+self.center_grav_x)*-1

        side_offset =self.wheeltrack/2 #repère ISO : x vers l'avant, y vers la gauche

        self.list_tires = [Tire(self,-side_offset,front_offset,not propulsion), #FR
            Tire(self,side_offset,front_offset, not propulsion),#FL
            Tire(self,-side_offset,rear_offset,propulsion),#RR
            Tire(self,side_offset,rear_offset,propulsion)] #RL

    def get_rect(self) -> pygame.Rect:
        """Calcule et renvoie le rectangle de collision pour la voiture."""
        centre_x = round(self.x - sind(self.angle) * self.center_grav_x * ppm)
        centre_y = round(self.y - cosd(self.angle) * self.center_grav_x * ppm)

        rect = pygame.Rect(0, 0, self.car_width * ppm, self.car_height * ppm)
        rect.center = (centre_x, centre_y)  # On positionne le centre ici !
        return rect


    def compute_new_metrics(self, input_dico):

        # torque_multiplier entre -1 et 1 : la logique d'incrémentation reste hard codée volontairement
        if input_dico["decelerate"]:
            if self.torque_multiplier > 0:
                self.torque_multiplier = -0.1
            else :
                self.torque_multiplier -= 0.05

        if input_dico["accelerate"]:
            if self.torque_multiplier < 0:
                self.torque_multiplier = 0.2 #l'acceleration commence pas a 0 pour la nervosité
            else :
                self.torque_multiplier += 0.05
        if (input_dico["accelerate"] and input_dico["decelerate"]) or (not input_dico["accelerate"] and not input_dico["decelerate"]) :
            self.torque_multiplier = 0 #si on ne fait rien ou on appuie sur les 2 : couple demandé est nul

        self.torque_multiplier = max(-1, min(1, self.torque_multiplier))
        self.desired_torque = self.compute_desired_torque() #en N.m

        if input_dico["turn_left"] and not input_dico["turn_right"]:
            self.turn_left()
        elif input_dico["turn_right"] and not input_dico["turn_left"]:
            self.turn_right()
        elif not input_dico["turn_left"] and not input_dico["turn_right"]:
            if self.steering_multiplier > 0 :
                self.steering_multiplier -= min(0.05, abs(self.steering_multiplier))
            if self.steering_multiplier < 0 :
                self.steering_multiplier += min(0.05, abs(self.steering_multiplier))

        self.steering_multiplier = max(-1, min(1, self.steering_multiplier))
        self.steering_angle = self.steering_multiplier * self.steering_range #en radians

    def compute_desired_torque(self) -> float:
        """ Couple demandé en N.m selon le multiplicateur et le sens de marche """
        if self.torque_multiplier > 0 and self.vx >= 0:
            return self.accelerate_forward_torque()
        if self.torque_multiplier > 0 and self.vx < 0:
            return self.brake_reverse_torque()
        if self.torque_multiplier < 0 and self.vx > 0:
            return self.brake_forward_torque()
        if self.torque_multiplier < 0 and self.vx <= 0:
            return self.accelerate_reverse_torque()
        return self.coasting_torque()

    def accelerate_forward_torque(self) -> float:
        return self.torque_multiplier * self.max_torque #positif

    def accelerate_reverse_torque(self) -> float:
        return self.torque_multiplier * self.max_torque #négatif

    def brake_forward_torque(self) -> float:
        return self.torque_multiplier * self.braking_torque #négatif, s'oppose à vx > 0

    def brake_reverse_torque(self) -> float:
        return self.torque_multiplier * self.braking_torque #positif, s'oppose à vx < 0

    def coasting_torque(self) -> float:
        return 0.0

    def turn_left(self) -> None:
        """ Braque à gauche, plus lentement quand le volant est déjà bien tourné """
        if self.steering_multiplier < 0.3 :
            self.steering_multiplier += self.steering_velocity
        else :
            self.steering_multiplier += self.steering_velocity/4

    def turn_right(self) -> None:
        """ Braque à droite, plus lentement quand le volant est déjà bien tourné """
        if self.steering_multiplier > -0.3 :
            self.steering_multiplier -= self.steering_velocity
        else :
            self.steering_multiplier -= self.steering_velocity/4

                    
    def update_position(self) -> None:
        """ Met à jour la position de la voiture en fonction de sa vitesse"""
        self.compute_speeds(self.compute_accelerations())
        dt = 1 / c.FPS
        self.angle += math.degrees(self.omegad) * dt #omega en rad/s, l'angle reste en degrés
        self.angle = self.angle%360
        #vitesses en m/s : conversion en pixels avec ppm
        self.x += (self.vx * sind(self.angle) + self.vy * cosd(self.angle)) * ppm * dt
        self.y += (self.vx * cosd(self.angle) - self.vy * sind(self.angle)) * ppm * dt

    def compute_accelerations(self):
        
        ax=0
        ay=0
        omegadd =0
        fx_tot =0
        fy_tot=0
        fx_car = 0
        fy_car = 0
        mom_tot = 0
        for tire in self.list_tires:
            fx,fy = tire.compute_forces()
            if tire.offset_length>0:
                fx_car = fx * math.cos(self.steering_angle) - fy*math.sin(self.steering_angle)
                fy_car = fx * math.sin(self.steering_angle) + fy*math.cos(self.steering_angle)
            else :
                fx_car = fx
                fy_car = fy

            fx_tot += fx_car
            fy_tot +=fy_car

            mom_tot += tire.offset_length * fy_car - tire.offset_width * fx_car
        fx_tot -= self.vx *abs(self.vx) * 0.5 + 0.3 * self.vx #friction du a l'air (vitesse carrée) et linéaire (vitesse lineaire)
       
        ax = fx_tot/self.mass + self.omegad*self.vy #le terme de rotation des vecteurs vitesse était oublié : la voiture pouvait garder sa vitesse vx dans les virages sans cout
        ay = fy_tot/self.mass - self.omegad*self.vx


        omegadd = mom_tot/self.izz 
        return (ax,ay,omegadd)

    def compute_speeds(self,accels) -> float:
        """calcule les vitesses en x et en y ainsi que la vitesse angulaire pour servir lors de la mise a jour de la position"""
        dt = 1 / c.FPS
        self.vx += accels[0] * dt #m/s
        self.vy += accels[1] * dt #m/s
        self.omegad += accels[2] *dt #rad/s
        if abs(self.vx) < 0.05 and self.desired_torque == 0:
            self.vx = 0
       

    def engine_behavior(self, tire_speed):
        """Sert a plafonner la vitesse du moteur (le couple), retourne un multiplicateur pour le couple moteur"""
        x = min(abs(tire_speed) * self.final_drive / self.engine_speed_max, 1)
        return 1 - x**5

    
    def build_sprite(self, chosen_car) -> pygame.Surface:
        """ Construit et retourne la surface graphique (sprite) de la voiture """
        
        directory = "assets/sprites/cars"
        files = []
        for name in sorted(os.listdir(directory)):
            if name.endswith(".png"):
                path = os.path.join(directory, name)
                files.append(path)
        chosen_sprite = pygame.image.load(files[chosen_car]).convert_alpha() #sprite a la bonne taille
        chosen_sprite = pygame.transform.scale(chosen_sprite,(self.car_width*ppm,self.car_height*ppm))
        return chosen_sprite

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """ Calcule et retourne le sprite pivoté selon l'angle actuel ainsi que son rectangle centré positionné pour l'affichage """

        # Rotation de l'image de base (le moins a été retiré, afin de convenir au sens trigonométrique)
        rotated = pygame.transform.rotate(self.sprite, self.angle)

        # Recalcule le rectangle de l'image en fixant son centre exact sur les coordonnées (x,y) de la voiture offset par le cg (indispensable car une rotation va modifier les dimensions globales de l'image)
        rect = rotated.get_rect(center=(round(self.x - sind(self.angle)*self.center_grav_x*ppm), round(self.y - cosd(self.angle)*self.center_grav_x*ppm)))

        return rotated, rect

    def debug_variables(self,font) -> pygame.Surface:
        #FOR DEBUGGING TO REMOVE LATER ON
        surf_text = font.render(f"vx: {self.vx:.2f}  vy: {self.vy:.2f}  angle: {self.angle:.1f}  desired_torque: {self.desired_torque:.2f}  steering: {self.steering_angle:.3f}", True, (255, 255, 255))
        return surf_text