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

        self.contact_point_vel() 

        sx,sy,s_combined = self.compute_slips()

        Fx = self.magic_tire_formulaLONGI(friction_coef, self.Fz, sx, sy, s_combined)
        Fy = self.magic_tire_formulaLATE(friction_coef, self.Fz, sx, sy, s_combined)
        self.compute_rot_speed_tire(Fx)
                        
        
        
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
            
    def contact_point_vel(self):
        self.vcx = self.car.vx + self.car.omegad * -self.offset_width
        self.vcy = self.car.vy + self.car.omegad * self.offset_length


    def magic_tire_formulaLONGI(self,friction, Fz,sx,sy,s_combined): #sy pas utilisé mais c'est pour que les calls soient identique plus haut, idemm pour late
        """Force longitudinale (formule de Pacejka) selon le glissement combiné, projetée sur l'axe x"""
        if s_combined < 1e-6: #évite la division par 0 quand il n'y a aucun glissement
            return 0
        bx = c.PACEJKA_B_LONG * s_combined
        inner = bx - c.PACEJKA_E_LONG * (bx - math.atan(bx))
        F = friction * Fz * math.sin(c.PACEJKA_C_LONG * math.atan(inner)) #Formule magique du pneu, extrait de TireModelingReader 2023 (Igo Besselink, université d'Eindhoven)
        return F * sx / s_combined #part de la force sur l'axe x

    def magic_tire_formulaLATE(self,friction, Fz,sx,sy,s_combined):
        """Force latérale (formule de Pacejka) selon le glissement combiné, projetée sur l'axe y"""
        if s_combined < 1e-6:
            return 0
        by = c.PACEJKA_B_LAT * s_combined
        inner = by - c.PACEJKA_E_LAT * (by - math.atan(by))
        F = friction * Fz * math.sin(c.PACEJKA_C_LAT * math.atan(inner))
        return -F * sy / s_combined #il y a un moins car la vitesse late de la roue est toujrous nulel donc le slip fait -v_late - a opposers

    def compute_Fz(self): #POUR PLUS TARD
        self.Fz = self.Fz  

    def compute_slips(self) :

        if self.offset_length>0: #seulement si ce sont les pneus qui sont devant
            v_longi = self.vcx * math.cos(self.car.steering_angle) + self.vcy * math.sin(self.car.steering_angle)
            v_late = -self.vcx * math.sin(self.car.steering_angle) + self.vcy * math.cos(self.car.steering_angle) #Vitesses a convertir dans le referentiel du pneu
        else :
            v_longi = self.vcx
            v_late = self.vcy

        #vitesses du point de contact du pneu dans le ref de la voiture obtenues -> QUID du pneu lui meme ? Il tourne ou pas ?
        v_ref = max(1,abs(v_longi)) #vitesse qui permet d'avoir un slip RATIO (dérapage a 1m/s plus violent en roulant a 20 kmh que a 120 kmh)
        slip_longi = (self.rot_speed_tire * self.tire_radius -v_longi)/v_ref
        slip_late = math.atan(v_late/v_ref)
        combined_slip = math.sqrt(slip_longi**2 + slip_late**2)
        return slip_longi, slip_late, combined_slip