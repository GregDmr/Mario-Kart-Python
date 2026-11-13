import pygame
import math
import os
import constants as c
from constants import PIXEL_PER_METER as ppm
from model.tire import Tire
from tools.degree_trig import sind, cosd
class Car:

    def __init__(self, start_col: int, start_row: int, chosen_car : int =0):
        """ Initialise une voiture à partir de sa position sur la grille """

        #Attributs
        self.mass = c.MASS[chosen_car]
        self.wheelbase = c.WHEEL_BASE[chosen_car]
        self.wheeltrack = c.WHEEL_TRACK[chosen_car]
        self.center_grav_x = c.CENTER_GRAVITY_X[chosen_car]
        self.center_grav_z = c.CENTER_GRAVITY_Z[chosen_car]
        self.car_height = c.CAR_HEIGHT[chosen_car]
        self.car_width = c.CAR_WIDTH[chosen_car]
        self.steering_velocity = c.STEERING_VELOCITY[chosen_car]
        self.max_torque = c.MAX_ENGINE_TORQUE[chosen_car]
        self.final_drive = 10
        self.braking_torque = 300 #attention meme ordre de grandeur que engine torque (plus grand car freinage, mais le calcul pour la force est le meme)
        self.izz = c.CAR_IZZ[chosen_car]
        propulsion = c.RWD[chosen_car]
        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * c.TILE_SIZE + c.TILE_SIZE // 2
        self.y = start_row * c.TILE_SIZE + c.TILE_SIZE // 2

        # Initialisation vitesse et angle
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.omegad :float = 0.0
        self.angle: float = 0.0
        self.steering_angle : float = 0.0
        self.desired_torque : float = 0.0
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

    def compute_new_metrics(self, input_dico):

        if input_dico["decelerate"]: #La réponse de l'accelerateur est hard codé volontairement, moins d'importance que le steering angle donc reste constant
            if self.desired_torque > 0:
                self.desired_torque = -0.1
            else :
                self.desired_torque -=0.05

        if input_dico["accelerate"]:
            if self.desired_torque < 0:
                self.desired_torque = 0.2 #l'acceleration commence pas a 0 pour la nervosité
            else :
                self.desired_torque +=0.05      
        if (input_dico["accelerate"] and input_dico["decelerate"]) or (not input_dico["accelerate"] and not input_dico["decelerate"]) :
            self.desired_torque = 0 #si on ne fait rien ou on appuie sur les 2 : couple demandé est nul

        if input_dico["turn_left"] or input_dico["turn_right"] :
            if input_dico["turn_left"] and input_dico["turn_right"]:
                self.steering_angle = self.steering_angle
            if input_dico["turn_left"] and not input_dico["turn_right"]:
                if self.steering_angle<0.3 :
                     self.steering_angle+=self.steering_velocity
                else :
                    self.steering_angle+=self.steering_velocity/4
            if input_dico["turn_right"] and not input_dico["turn_left"]:
                if self.steering_angle>-0.3 :
                    self.steering_angle-=self.steering_velocity
                else :
                    self.steering_angle-=self.steering_velocity/4

        if not (input_dico["turn_left"] or input_dico["turn_right"]):
            if self.steering_angle >0 :
                self.steering_angle -= min(0.05, abs(self.steering_angle))
            if self.steering_angle <0 :
                            self.steering_angle += min(0.05, abs(self.steering_angle))

        if self.desired_torque >0 :
             self.desired_torque = min(self.desired_torque, 1)
        if self.desired_torque <0 :
                     self.desired_torque = max(self.desired_torque, -1)

        if self.steering_angle >0 :
                     self.steering_angle = min(self.steering_angle, 1)
        if self.steering_angle <0 :
                     self.steering_angle = max(self.steering_angle, -1)

                    
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
        mom_tot = 0
        for tire in self.list_tires:
            fx,fy = tire.compute_forces()
            fx_tot+= fx
            fy_tot+= fy
            mom_tot += tire.offset_length * fy - tire.offset_width * fx

        ax=fx_tot/self.mass
        ay = fy_tot/self.mass

        #omegadd = mom_tot/self.izz POUR PLUS TARD
        return (ax,ay,omegadd)

    def compute_speeds(self,accels) -> float:
        """calcule les vitesses en x et en y ainsi que la vitesse angulaire pour servir lors de la mise a jour de la position"""
        dt = 1 / c.FPS
        self.vx += accels[0] * dt #m/s
        self.vy += accels[1] * dt #m/s
        self.omegad = self.steering_angle *3
        #self.omegad += accels[2] * dt #rad/s POUR PLUS TARD
    
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