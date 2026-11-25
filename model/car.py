import pygame
import math
import os
import constants as c
from constants import PIXEL_PER_METER as ppm
from model.tire import Tire
from tools.degree_trig import sind, cosd
from model.circuit import Circuit
import random
class Car:
    """Voiture : physique, pneus, traces de pneus et sprite."""

    def __init__(self, circuit :Circuit, start_col: int, start_row: int, chosen_car : int =0, start_angle: float = 0.0):
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
        self.wheel_length = c.WHEEL_LENGTH[chosen_car]
        self.wheel_width = c.WHEEL_WIDTH[chosen_car]
        self.steering_velocity = c.STEERING_VELOCITY[chosen_car]
        self.steering_range = c.STEERING_RANGE[chosen_car]
        self.max_torque = c.MAX_ENGINE_TORQUE[chosen_car]
        self.braking_torque = c.MAX_BRAKING_TORQUE[chosen_car] #attention meme ordre de grandeur que engine torque (plus grand car freinage, mais le calcul pour la force est le meme)
        self.izz = c.CAR_IZZ[chosen_car]
        self.tire_radius = c.TIRE_RADIUS[chosen_car]
        self.wheel_inertia = c.WHEEL_INERTIA[chosen_car]
        propulsion = c.RWD[chosen_car]
        self.final_drive = c.FINAL_DRIVE[chosen_car]
        self.engine_speed_max = 750 #les deux valeurs a equilibrer en essais.
        # Conversion des coordonnées de la grille en pixels
        self.x = start_col * c.TILE_SIZE + c.TILE_SIZE // 2
        self.y = start_row * c.TILE_SIZE + c.TILE_SIZE // 2
        self.fz_ax = 0
        self.fz_ay = 0
        # Initialisation vitesse et angle
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.omegad :float = 0.0
        self.angle: float = start_angle #degrés
        self.steering_multiplier : float = 0.0 #entre -1 et 1
        self.steering_angle : float = 0.0 #radians
        self.torque_multiplier : float = 0.0 #entre -1 et 1
        self.desired_torque : float = 0.0 #N.m
        # Génération du sprite visuel de base 
        self.sprite = self.build_sprite(chosen_car)
        self.tire_mark_list = []
        #Pneus
        front_offset = self.wheelbase/2-self.center_grav_x
        rear_offset = (self.wheelbase/2+self.center_grav_x)*-1

        side_offset =self.wheeltrack/2 #repère ISO : x vers l'avant, y vers la gauche

        self.list_tires = [Tire(self,-side_offset,front_offset,not propulsion), #FR
            Tire(self,side_offset,front_offset, not propulsion),#FL
            Tire(self,-side_offset,rear_offset,propulsion),#RR
            Tire(self,side_offset,rear_offset,propulsion)] #RL

        #sondes de collision pour ne pas recalculer a chaque trigger_colision
        self.L_probe_px = 15
        self.N_probes = 24
        self.list_angles = []
        self.normal_vec = []
        for k in range(self.N_probes):
            angle = k*(360/self.N_probes)
            self.list_angles.append(angle)
            self.normal_vec.append((sind(angle), -cosd(angle)))

    def get_rect(self) -> pygame.Rect:
        """Calcule et renvoie le rectangle de collision pour la voiture."""
        centre_x = round(self.x - sind(self.angle) * self.center_grav_x * ppm)
        centre_y = round(self.y - cosd(self.angle) * self.center_grav_x * ppm)

        rect = pygame.Rect(0, 0, self.car_width * ppm, self.car_height * ppm)
        rect.center = (centre_x, centre_y)  # On positionne le centre ici !
        return rect

    def calcul_vitesse_abs(self):
        """ Renvoie la vitesse absolue de la voiture qui sert pour l'envoie des items """
        return math.hypot(self.vx, self.vy)

    def compute_new_metrics(self, input_dico):

        # torque_multiplier entre -1 et 1 : la logique d'incrémentation reste hard codée volontairement
        if input_dico["decelerate"]:
            if self.torque_multiplier > 0:
                self.torque_multiplier = -0.3
            else :
                self.torque_multiplier -= 0.1

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
        speed_factor = 1 / (1 + (self.vx / c.STEERING_SPEED_REF)**2) #1 a l'arret, 0.5 a la vitesse de reference
        self.steering_angle = self.steering_multiplier * self.steering_range * speed_factor #en radians

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
        self.tire_mark_list = [m for m in self.tire_mark_list if m.lifespan > 0] #itere dans la liste, mais ne valide pas la classe si lifespan =0 ou moins
        accels = self.compute_accelerations()
        #ICI UNE FONCTION QUI OVERWRITE LES ACCELERATIONS POUR LES ITEMS (PLUS SOFT QUE VX)
        self.compute_speeds(accels)
        dt = 1 / c.FPS
        ## AJOUTE LE STUFF POUR LES ITEMS ICI, TU OVERWRITE VX / VY / OMEGAD, EN VERIFIANT SI ON EST AFFECTE PAR UN ITEM
        
        
        self.angle += math.degrees(self.omegad) * dt #omega en rad/s, l'angle reste en degrés
        self.angle = self.angle%360
        #vitesses en m/s : conversion en pixels avec ppm
        self.x += (self.vx * sind(self.angle) + self.vy * cosd(self.angle)) * ppm * dt
        self.y += (self.vx * cosd(self.angle) - self.vy * sind(self.angle)) * ppm * dt
        
        #coins de la carrosserie en pixels, mesurés depuis le CG (comme pour les pneus)
        front = self.car_height/2 - self.center_grav_x
        rear = -(self.car_height/2 + self.center_grav_x)
        side = self.car_width/2
        sin_a = sind(self.angle)
        cos_a = cosd(self.angle)
        cornerFR = (self.x - ppm*side*cos_a + ppm*front*sin_a, self.y + ppm*side*sin_a + ppm*front*cos_a)
        cornerFL = (self.x + ppm*side*cos_a + ppm*front*sin_a, self.y - ppm*side*sin_a + ppm*front*cos_a)
        cornerRR = (self.x - ppm*side*cos_a + ppm*rear*sin_a, self.y + ppm*side*sin_a + ppm*rear*cos_a)
        cornerRL = (self.x + ppm*side*cos_a + ppm*rear*sin_a, self.y - ppm*side*sin_a + ppm*rear*cos_a)
        corner_list = [cornerFR,cornerFL,cornerRR,cornerRL]
        
        for corner in corner_list :
            tile = self.circuit.get_tile_at_pixel(corner[0],corner[1])
            if tile is not None :
                if tile.road_type == 2 :
                    self.trigger_colision(corner) 
                if tile.road_type == 4 :
                    self.angle += 0.2*self.vx * (-0.5+random.random()) #vibration sur les vibreurs, magnitude fine tune et hard codé

    def compute_accelerations(self):
        
        ax=0
        ay=0
        omegadd =0
        fx_tot =0
        fy_tot=0
        fx_car = 0
        fy_car = 0
        mom_tot = 0
        static_friction_tot = 0
        for tire in self.list_tires:
            fx,fy,tire_mark,static_friction = tire.compute_forces()
            static_friction_tot += static_friction

            if tire.offset_length>0:
                fx_car = fx * math.cos(self.steering_angle) - fy*math.sin(self.steering_angle)
                fy_car = fx * math.sin(self.steering_angle) + fy*math.cos(self.steering_angle)
            else :
                fx_car = fx
                fy_car = fy

            if tire_mark is not None : 
                self.render_tire_mark(tire_mark) # dans compute acceleration puisque le derapage du pneu est directement lié
            fx_tot += fx_car
            fy_tot +=fy_car
            mom_tot += tire.offset_length * fy_car - tire.offset_width * fx_car
        fx_tot -= self.vx *abs(self.vx) * c.AIR_RESISTANCE + c.ROLLING_RESISTANCE * self.vx #friction due a l'air (vitesse carrée) et au roulement (vitesse lineaire)
        static_friction = static_friction_tot / len(self.list_tires) #moyenne des pneus, selon le sol sous chacun
        if self.vx >= 0.2:
            fx_tot -= static_friction
        elif self.vx <= -0.2:
            fx_tot += static_friction #force constante du sol, pas appliquée à l'arrêt pour ne pas faire vibrer la voiture

        self.fz_ax = fx_tot/self.mass #accélérations réelles du corps, gardées pour le calcul de Fz à la frame suivante
        self.fz_ay = fy_tot/self.mass
        ax = self.fz_ax + self.omegad*self.vy #le terme de rotation des vecteurs vitesse était oublié : la voiture pouvait garder sa vitesse vx dans les virages sans cout
        ay = self.fz_ay - self.omegad*self.vx


        omegadd = mom_tot/self.izz 
        return (ax,ay,omegadd)

    def compute_speeds(self,accels) -> float:
        """calcule les vitesses en x et en y ainsi que la vitesse angulaire pour servir lors de la mise a jour de la position"""
        dt = 1 / c.FPS
        self.vx += accels[0] * dt #m/s
        self.vy += accels[1] * dt #m/s
        self.omegad += accels[2] *dt #rad/s
        if abs(self.vx) < 0.4 and self.desired_torque == 0 and self.steering_angle == 0  :
            self.vx = 0

        if abs(self.vy) < 0.4 and self.desired_torque == 0 and self.steering_angle == 0 :
            self.vy = 0
        
        if abs(self.omegad) < 0.05 and self.desired_torque == 0 and self.steering_angle == 0 :
            self.omegad = 0

    def engine_behavior(self, tire_speed):
        """Sert a plafonner la vitesse du moteur (le couple), retourne un multiplicateur pour le couple moteur"""
        x = min(abs(tire_speed) * self.final_drive / self.engine_speed_max, 1)
        return 1 - x**5

    
    def build_sprite(self, chosen_car) -> pygame.Surface:
        """ Construit et retourne la surface graphique (sprite) de la voiture """
        path = os.path.join(c.CAR_SPRITES_DIRECTORY, c.CAR_SPRITE[chosen_car])
        chosen_sprite = pygame.image.load(path).convert_alpha() #sprite a la bonne taille
        chosen_sprite = pygame.transform.scale(chosen_sprite,(self.car_width*ppm,self.car_height*ppm))

        #surface un peu plus grande que la voiture, pour que les roues puissent dépasser de la carrosserie
        self.sprite_pad = 3
        pad = self.sprite_pad
        sprite = pygame.Surface((chosen_sprite.get_width() + 2*pad, chosen_sprite.get_height() + 2*pad), pygame.SRCALPHA)
        sprite.blit(chosen_sprite, (pad, pad))

        #roue : rectangle sombre, grand côté dans le sens de roulage
        self.wheel = pygame.Surface((round(self.wheel_width*ppm), round(self.wheel_length*ppm)), pygame.SRCALPHA)
        self.wheel.fill((25, 25, 25))

        for side in (-1, 1):
            rect = self.wheel.get_rect(center=self.wheel_position(side, -1))
            sprite.blit(self.wheel, rect)
        return sprite

    def wheel_position(self, side, end) -> tuple[int, int]:
        """Centre d'une roue sur le sprite, voiture non tournée. side : -1 / 1 (un côté / l'autre), end : 1 avant, -1 arrière"""
        x = self.sprite_pad + self.car_width*ppm/2 + side * self.wheeltrack/2 * ppm
        y = self.sprite_pad + self.car_height*ppm/2 + end * self.wheelbase/2 * ppm
        return round(x), round(y)

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """ Calcule et retourne le sprite pivoté selon l'angle actuel ainsi que son rectangle centré positionné pour l'affichage """

        # Rotation de l'image de base (le moins a été retiré, afin de convenir au sens trigonométrique)
        #les roues avant tournent avec le braquage : dessinées sur une copie du sprite à chaque image
        frame = self.sprite.copy()
        front_wheel = pygame.transform.rotate(self.wheel, math.degrees(self.steering_angle))
        for side in (-1, 1):
            wheel_rect = front_wheel.get_rect(center=self.wheel_position(side, 1))
            frame.blit(front_wheel, wheel_rect)

        rotated = pygame.transform.rotate(frame, self.angle)

        # Recalcule le rectangle de l'image en fixant son centre exact sur les coordonnées (x,y) de la voiture offset par le cg (indispensable car une rotation va modifier les dimensions globales de l'image)
        rect = rotated.get_rect(center=(round(self.x - sind(self.angle)*self.center_grav_x*ppm), round(self.y - cosd(self.angle)*self.center_grav_x*ppm)))

        return rotated, rect

    def debug_variables(self,font) -> pygame.Surface:
        #FOR DEBUGGING TO REMOVE LATER ON
        surf_text = font.render(f"vx: {self.vx:.2f}  vy: {self.vy:.2f}  angle: {self.angle:.1f}  desired_torque: {self.desired_torque:.2f}  steering: {self.steering_angle:.3f}", True, (255, 255, 255))
        return surf_text    

    def render_tire_mark(self,tire_mark):
        self.tire_mark_list.append(tire_mark)

    def big_hit(self):
        """ Effet fake itembox et carapace verte / bleue """
        self.vx = 0
        self.vy = 0

    def trigger_colision(self,cornerTuple):
        colisionX = cornerTuple[0]
        colisionY = cornerTuple[1]
        x_coords = []
        y_coords = []

        for angle in self.list_angles :
            x_coords.append(colisionX + self.L_probe_px * sind(angle))
            y_coords.append(colisionY + self.L_probe_px * - cosd(angle))
        x_final = 0
        y_final = 0
        for i in range(self.N_probes):
            tile = self.circuit.get_tile_at_pixel(x_coords[i],y_coords[i])
            if tile is not None :
                if tile.road_type != 2:
                   x_final+= self.normal_vec[i][0]
                   y_final += self.normal_vec[i][1]
        length = math.sqrt(x_final**2 + y_final**2)
        
        if length > 1e-6 : #normaliser
            nx = x_final / length
            ny = y_final / length
            nx_car = nx*sind(self.angle) + ny*cosd(self.angle)
            ny_car = nx*cosd(self.angle) - ny*sind(self.angle)
        else :
            # fallback : uniquement si le mur est particulier, très fin , toutes les probes touchent le vide ou le mur
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed < 1e-6 :
                return
            nx_car = -self.vx / speed
            ny_car = -self.vy / speed

        bounce =0.3
        mu =0.1
        tx = -ny_car
        ty = nx_car
        vn = self.vx*nx_car + self.vy*ny_car      # vitesse dans la direction normale, imaginer, a quel point ma vitesse en X match avec la normale au mur, idem pour Y, et additionner
        vt = self.vx*tx + self.vy*ty              # vitesse le long du mur, idem en tangeante au mur
        if vn < 0 :
            vn = -bounce * vn                          # rebond
            vt = (1 - mu) * vt                    # frottement
            self.vx = vn*nx_car + vt*tx
            self.vy = vn*ny_car + vt*ty
        
        
        
       




    def slide(self):
        """ Effet glissage pour banane, flaque d'huile"""
        pass

    def boost(self):
        """ Effet accélération champignon / boostpad"""
        pass

    def special_effect(self):
        """ Effet spécial pour l'étoile, un peu plus rapide et peut être rendre la voiture plsu maniable"""
    