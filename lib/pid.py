class PID:

    def __init__ (self, KP, KI, KD):

        #self.KP = 0.08
        #self.KI = 0.01
        #self.KD = 0.01

        self.KP = KP
        self.KI = KI
        self.KD = KD

        self.prev_error = 0
        self.sum_error = 0


    def set_proportional (self, value):
        self.KP = value


    def get_proportional (self):
        return self.KP


    def set_integral (self, value):
        self.KI = value


    def get_integral (self):
        return self.KI


    def set_derivative (self, value):
        self.KD = value


    def get_derivative (self):
        return self.KD


    def reset (self):
        self.prev_error = 0
        self.sum_error = 0
        

    def update (self, current_speed, target_speed):

        error = target_speed - current_speed

        current_speed += (error * self.KP) + (self.prev_error * self.KD) + (self.sum_error * self.KI)
        current_speed = max(min(1, current_speed), 0) # clamp the value between 0 and 1
        
        self.prev_error = error
        self.sum_error += error

        return current_speed
