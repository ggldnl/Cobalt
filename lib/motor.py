from pid import PID
from encoder import Encoder
from hardlib.DRV8833.DRV8833 import DRV8833
import logging

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('MOTOR')
logger.setLevel(logging.DEBUG)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.DRV8833 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger


# --------------------------- encoder core library --------------------------- #

class Motor:
    """
        
    """

    def __init__ (self,
                  # encoder pins
                  PIN_CLK,
                  PIN_DT,
                  # motor pins
                  IN_1_A, IN_2_A,
                  IN_1_B, IN_2_B,
                  ENABLE,
                  channel,
                  # PID
                  KP, KI, KD
                ):
        
        #self.PIN_CLK = PIN_CLK
        #self.PIN_DT = PIN_DT
        #self.IN_1_A = IN_1_A
        #self.IN_2_A = IN_2_A
        #self.IN_1_B = IN_1_B
        #self.IN_2_B = IN_2_B  
        #self.ENABLE = ENABLE

        self.DRV8833 = DRV8833 (
            IN_1_A = IN_1_A, IN_2_A = IN_2_A,
            IN_1_B = IN_1_B, IN_2_B = IN_2_B,
            ENABLE = ENABLE
        )
        self.channel = channel

        self.encoder = Encoder (
            PIN_CLK = PIN_CLK,
            PIN_DT = PIN_DT
        )

        self.pid = PID (
            KP = KP,
            KI = KI,
            KD = KD
        )


    def move (self, speed):

        speed = max(-1.0, min(1.0, speed)) # gives a number in range [-1.0, 1.0]
        self.DRV8833.write(self.channel, speed)

    
    def close (self):
        self.encoder.close()
        self.DRV8833.close()


    def __del__ (self):
        self.close()


    def __enter__ (self):
        pass


    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            #logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True


if __name__ == '__main__':

    with Motor (
        # motor pins
        IN_1_A = 21, IN_2_A = 20,
        IN_1_B = 16, IN_2_B = 12,
        ENABLE = 7,
        # encoder pins
        PIN_CLK = 25,
        PIN_DT = 8,
        # PID
        KP = 0.08,
        KI = 0.01,
        KD = 0.01
    ) as motor:
        pass        


# backward speed (0, 1)
# forward speed (0, 1)
# move speed (-1, 1)
# returns encoder
