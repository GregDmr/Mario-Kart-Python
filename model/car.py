import pygame
import math
import os
import constants as c


class Car:

    def __init__(self, start_col: int, start_row: int, chosen_car : int =0):
        """ Initialise une voiture à partir de sa position sur la grille """

        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * c.TILE_SIZE + c.TILE_SIZE // 2
        self.y = start_row * c.TILE_SIZE + c.TILE_SIZE // 2

        # Initialisation vitesse et angle
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.angle: float = 0.0
        self.steering_angle : float = 0.0
        self.desired_torque : float = 0.0
        self.angle : float =0.0
        self.chosen_car = chosen_car
        # Génération du sprite visuel de base 
        self.sprite = self.build_sprite(chosen_car)

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
                     self.steering_angle+=c.STEERING_VELOCITY[self.chosen_car]
                else :
                    self.steering_angle+=c.STEERING_VELOCITY[self.chosen_car]/4
            if input_dico["turn_right"] and not input_dico["turn_left"]:
                if self.steering_angle>0.3 :
                    self.steering_angle-=c.STEERING_VELOCITY[self.chosen_car]
                else :
                    self.steering_angle-=c.STEERING_VELOCITY[self.chosen_car]/4

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
        self.compute_speeds()
        self.angle += self.omega #oméga dans le futur sera en radian, a convertir pour pygame. La gestuelle sera peut etre complexe
        self.angle = self.angle%360
        self.x += self.vx * math.sin(self.angle/360*2*math.pi) + self.vy * math.cos(self.angle/360*2*math.pi)
        self.y += self.vx * math.cos(self.angle/360*2*math.pi) + self.vy * math.sin(self.angle/360*2*math.pi)
        

    def compute_speeds(self) -> float:
        """calcule les vitesses en x et en y ainsi que la vitesse angulaire pour servir lors de la mise a jour de la position"""
        self.vx = self.desired_torque * 5
        self.omega = self.steering_angle * 3
    
    def build_sprite(self, chosen_car) -> pygame.Surface:
        """ Construit et retourne la surface graphique (sprite) de la voiture """
        
        directory = "assets/sprites/cars"
        files = []
        for name in sorted(os.listdir(directory)):
            if name.endswith(".png"):
                path = os.path.join(directory, name)
                files.append(path)
        chosen_sprite = pygame.image.load(files[chosen_car]).convert_alpha() #sprite a la bonne taille
        chosen_sprite = pygame.transform.scale(chosen_sprite,(c.CAR_WIDTH,c.CAR_HEIGHT))
        return chosen_sprite

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """ Calcule et retourne le sprite pivoté selon l'angle actuel ainsi que son rectangle centré positionné pour l'affichage """

        # Rotation de l'image de base (le moins a été retiré, afin de convenir au sens trigonométrique)
        rotated = pygame.transform.rotate(self.sprite, self.angle)

        # Recalcule le rectangle de l'image en fixant son centre exact sur les coordonnées (x,y) de la voiture (indispensable car une rotation va modifier les dimensions globales de l'image)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))

        return rotated, rect

    def debug_variables(self,font) -> pygame.Surface:
        #FOR DEBUGGING TO REMOVE LATER ON
        surf_text = font.render(f"vx: {self.vx:.2f}  vy: {self.vy:.2f}  angle: {self.angle:.1f}  desired_torque: {self.desired_torque:.2f}  steering: {self.steering_angle:.3f}", True, (255, 255, 255))
        return surf_text