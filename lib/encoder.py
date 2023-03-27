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

        # for now, only one pin is used and the direction in which the 
        # motor is spinning can not be inferred.
        # TODO -> use both pins
        GPIO.add_event_detect(self.PIN_A, GPIO.RISING, callback=self._increment)

        logger.debug('Setup done')


    def reset(self):
        
        logger.debug('Reset ticks')

        self._value = 0


    def _increment(self):
        self._value += 1


    def read(self):
        return self._value
    

    def close (self):
        """
        Frees the GPIO resources.
        """
        logger.info('GPIO cleanup')

        # calling GPIO.cleanup() will affect all the pins,
        # even the ones used in other modules
        # GPIO.cleanup()
        GPIO.setup(self.PIN_A, GPIO.IN)
        GPIO.setup(self.PIN_B, GPIO.IN)


    def __enter__(self):
        return self


    def __del__ (self):
        # self.close()
        pass


    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True


# ----------------------------------- main ----------------------------------- #


if __name__ == '__main__':

    # ------------------------------- logger setup ------------------------------- #

    # create a logger instance
    logger = logging.getLogger('MAIN')
    logger.setLevel(logging.INFO)

    # create a formatter instance
    formatter = logging.Formatter(
        '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'
        )

    # create a handler instance
    handler = logging.FileHandler('../../log/cobalt.log', 'w')
    # handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # -------------------------------- actual test ------------------------------- #

    from time import sleep

    sampling_rate = 0.1 # read the encoder value once every 0.1 seconds

    with Encoder(
        PIN_A = 7,  # TODO fix
        PIN_B = 8
    ) as encoder:

        val = encoder.read()
        print('Encoder ticks: {}'.format(val))

        sleep(sampling_rate)
