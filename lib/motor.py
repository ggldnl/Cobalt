from pid import PID
from encoder import Encoder
from hardware_lib.DRV8833.DRV8833 import DRV8833

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
        self.encoder = Encoder (
            PIN_CLK = PIN_CLK,
            PIN_DT = PIN_DT
        )

        self.pid = PID (
            KP = KP,
            KI = KI,
            KD = KD
        )

        # assign a channel


    def forward (self):
        pass


    def backward (self):
        pass


    def stop (self):
        pass

    
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
