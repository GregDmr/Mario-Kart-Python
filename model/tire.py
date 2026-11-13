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

    def compute_forces(self):
        #offsets en mètres (x avant, y gauche), position de la voiture en pixels
        pos_x = self.car.x + ppm*self.offset_width*cosd(self.car.angle) + ppm*self.offset_length*sind(self.car.angle)
        pos_y = self.car.y - ppm*self.offset_width*sind(self.car.angle) + ppm*self.offset_length*cosd(self.car.angle)
        
        Fx=0
        Fy=0
        
        if self.car.desired_torque>0 and self.drived:
            Fx = self.car.desired_torque*self.car.final_drive * self.car.max_torque/(2*self.tire_radius)
        elif self.car.desired_torque<0:
            Fx = (self.car.desired_torque*self.car.final_drive * self.car.max_torque/(2*self.tire_radius))

        Fx-= self.car.vx * 25 #trainée basique pour frottement
        Fy = 0
        return (Fx,Fy)

