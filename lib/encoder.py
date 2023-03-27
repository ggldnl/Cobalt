import RPi.GPIO as GPIO
import logging

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('ENCODER')
logger.setLevel(logging.DEBUG)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.DRV8833 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger


# --------------------------- encoder core library --------------------------- #


class Encoder:

    def __init__(self, PIN_A, PIN_B):

        self.PIN_A = PIN_A
        self.PIN_B = PIN_B

        logger.debug('PIN_A set to {}'.format(PIN_A))
        logger.debug('PIN_B set to {}'.format(PIN_B))

        self._value = 0

    
    def _setup(self):
        """
        Sets up the hardware by setting the pins as INPUT.
        """
                
        logger.info('Starting hardware setup')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # init the library

        GPIO.setup(self.PIN_A, GPIO.IN)
        GPIO.setup(self.PIN_B, GPIO.IN)

        logger.debug('Setup done')

    
    def reset(self):
        self._value = 0


    def _increment(self):
        self._value += 1


    def read(self):
        return self._value