from DRV8833 import DRV8833
from DRV8833 import Decay

class MotorDriver:
    """
    Higher level class that manages DRV8833 (hardware library). 
    The DRV8833 board can control two brushed motors on two channels 
    or a single stepper motor. The DRV8833 library has no way of 
    controlling how many objects refer to it: multiple objects could 
    use it simultaneously. We want to ensure secure access, so that 
    only two objects can use it at the same time. This library manages 
    the two channels of the DRV8833 by returning two Motor objects, 
    one on each channel.
    """


    def __init__(self,
                IN_1_A, IN_2_A,         # control pins for left motor
                IN_1_B, IN_2_B,         # control pins for right motor
                ENABLE,                 # control pin to enable the board
                decay = Decay.SLOW,     # decay mode
                pwm_rate = 1000):       # frequency

        # create a DRV8833 object. This reperesent the physical component
        self.DRV8833 = DRV8833(
            IN_1_A, IN_2_A,
            IN_1_B, IN_2_B,
            ENABLE,
            decay = decay,
            pwm_rate = pwm_rate
        )
        self.channel_A = False
        self.channel_B = False


    # returns a motor using channel A at first and when not availabe when
    # not available. Throws an exception if there are no more available
    # channels   
    def get_motor (channel):
        
        if not self.channel_A
            self.channel_A = True
            return Motor(self.DRV8833, 'A') 
    
        


    def get_channel (channel):
        pass


if __name__ == '__name__':

    motor_driver = MotorDriver ()
    left = motor_driver.get_motor()
    right = motor_driver.get_motor()

    try:

        # this should yield an exception since a single DRV8833 
        # can be used to control only two brushed motors
        third = motor_driver.get_motor()
    
    except:
        pass

    import time
    interval = 10 # seconds
    t_end = time.time() + interval

    while time.time() < t_end:

        left.write()
        right.write()
