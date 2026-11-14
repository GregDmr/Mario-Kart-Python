import math
import constants as c
from constants import PIXEL_PER_METER as ppm
from tools.degree_trig import sind, cosd

class Tire :

    def __init__(self, car, offset_width : float, offset_length: float, drived :bool):
        self.car = car
        self.offset_width = offset_width
        self.offset_length = offset_length
        self.drived = drived
        self.tire_radius = 0.3
        #charge au repos : part du poids opposée à l'essieu du pneu, partagée entre les 2 pneus de l'essieu
        self.Fz = car.mass * c.GRAVITY * (car.wheelbase - abs(offset_length)) / (2 * car.wheelbase)
        self.rot_speed_tire = 0.0
        self.rot_speed_car = 0.0
        self.inertia = 1.2
    def compute_forces(self):

        tile = self.get_tile()
        if tile is not None:
            friction_coef = c.FRICTION_COEFFS[tile.road_type]
        else :
            friction_coef = c.FRICTION_COEFFS[1]
        self.compute_Fz()

        self.compute_rot_speed_car() 

        Fx = self.magic_tire_formula(friction_coef, self.Fz)

        self.compute_rot_speed_tire(Fx)
                        
        Fy = 0
        
        return (Fx,Fy)

    def get_tile(self):
        """Retourne un objet RoadTile pour le pneu contenant les attributs nécéssaires"""

        pos_x = self.car.x + ppm*self.offset_width*cosd(self.car.angle) + ppm*self.offset_length*sind(self.car.angle)
        pos_y = self.car.y - ppm*self.offset_width*sind(self.car.angle) + ppm*self.offset_length*cosd(self.car.angle)
        current_tile = self.car.circuit.get_tile_at_pixel(pos_x,pos_y) #objet RoadTile
        return current_tile

    def compute_rot_speed_tire(self,Fx):
        dt = 1/c.FPS
        torque = 0 #couple moteur appliqué à ce pneu
        brake_torque = 0 #couple de freinage, toujours positif
        if self.car.desired_torque>0 and self.drived and self.car.vx>=0: #accélération marche avant
            engine_factor = self.car.engine_behavior(self.rot_speed_tire)
            torque = self.car.desired_torque * self.car.final_drive/2 * engine_factor
        elif self.car.desired_torque>0 and self.car.vx<0: #freinage en marche arrière
            brake_torque = abs(self.car.desired_torque) * self.car.final_drive/4 #sur les 4 pneus, mais valeurs de braking torque arbitraires anyways
        elif self.car.desired_torque<0 and self.car.vx>0: #freinage en marche avant
            brake_torque = abs(self.car.desired_torque) * self.car.final_drive/4 #idem
        elif self.car.desired_torque<0 and self.car.vx<=0 and self.drived: #accélération marche arrière
            engine_factor = self.car.engine_behavior(self.rot_speed_tire)
            torque = self.car.desired_torque*self.car.final_drive/2*engine_factor

        self.rot_speed_tire += (torque - Fx * self.tire_radius) / self.inertia * dt #applique la correction de la force sol->roue quoi qu'il arrive
        #mais n'applique pas de ralentissement lors du freinage, il est fait plus loin

        #le frein s'oppose à la rotation de la roue, sans la faire repartir dans l'autre sens
        if brake_torque > 0:
            brake_step = brake_torque / self.inertia * dt
            if abs(self.rot_speed_tire) <= brake_step:
                self.rot_speed_tire = 0
            elif self.rot_speed_tire > 0:
                self.rot_speed_tire -= brake_step
            else:
                self.rot_speed_tire += brake_step #le freinage ne peut que s'opposer a la vitesse de la roue.
            
    def compute_rot_speed_car(self):
        self.rot_speed_car = self.car.vx/self.tire_radius

    def magic_tire_formula(self,friction, Fz):
        """Force longitudinale (formule de Pacejka) selon le taux de glissement"""
        slip_ratio = (self.rot_speed_tire - self.rot_speed_car) * self.tire_radius / max(abs(self.car.vx), 1) #max pour éviter la division par 0 à l'arrêt
        bx = c.PACEJKA_B_LONG * slip_ratio
        inner = bx - c.PACEJKA_E_LONG * (bx - math.atan(bx))
        return friction * Fz * math.sin(c.PACEJKA_C_LONG * math.atan(inner)) #Formule magique du pneu, extrait de TireModelingReader 2023 (Igo Besselink, université d'Eindhoven)
    
    def compute_Fz(self): #POUR PLUS TARD
        self.Fz = self.Fz