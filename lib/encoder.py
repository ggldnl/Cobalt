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


import enum

class Direction(enum.Enum):
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1


class Encoder:

    def __init__(self, PIN_CLK, PIN_DT, direction = Direction.CLOCKWISE):

        self.PIN_CLK = PIN_CLK # clock
        self.PIN_DT = PIN_DT # data

        logger.debug('PIN_CLK set to {}'.format(PIN_CLK))
        logger.debug('PIN_DT set to {}'.format(PIN_DT))

        self._count = 0
        self._direction = direction
        self._current_clk = 0 # current clock value (A)
        self._last_clk = 0 # last clock value

        self._setup()

    
    def _setup(self):
        """
        Sets up the hardware by setting the pins as INPUT.
        """
                
        logger.info('Starting hardware setup')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # init the library

        GPIO.setup(self.PIN_CLK, GPIO.IN)
        GPIO.setup(self.PIN_DT, GPIO.IN)

        GPIO.add_event_detect(self.PIN_CLK, GPIO.FALLING, callback=self._update)
        GPIO.add_event_detect(self.PIN_DT, GPIO.FALLING, callback=self._update)

        logger.debug('Setup done')


    def _update(self, channel):
        
        logger.debug('Updating encoder')

        self._current_clk = GPIO.input(self.PIN_CLK)

        if (self._current_clk != self._last_clk and 
            self._current_clk == GPIO.HIGH):

            self._count -= 1
            self._direction = Direction.COUNTERCLOCKWISE

        else:

            self._count += 1
            self._direction = Direction.CLOCKWISE
        
        self._last_clk = self._current_clk


    def reset(self):
        logger.debug('Reset encoder ticks')
        self._count = 0


    def read_count(self):
        return self._count


    def read_direction(self):
        return self._direction


    def close (self):
        """
        Frees the GPIO resources.
        """
        logger.info('GPIO cleanup')

        # calling GPIO.cleanup() will affect all the pins,
        # even the ones used in other modules
        # GPIO.cleanup()
        GPIO.setup(self.PIN_CLK, GPIO.IN)
        GPIO.setup(self.PIN_DT, GPIO.IN)


    def __enter__(self):
        return self


    def __del__ (self):
        self.close()
        

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
    logger.setLevel(logging.DEBUG)

    # create a formatter instance
    formatter = logging.Formatter(
        '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'
        )

    # create a handler instance
    handler = logging.FileHandler('../log/encoder.log', 'w')
    # handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # -------------------------------- parameters -------------------------------- #

    import configparser

    config = configparser.ConfigParser()
    config.read('../config/config.ini')

    LEFT_ENC_CLK = int(config['PINS']['LEFT_ENC_CLK'])
    LEFT_ENC_DT = int(config['PINS']['LEFT_ENC_DT'])
    RIGHT_ENC_CLK = int(config['PINS']['RIGHT_ENC_CLK'])
    RIGHT_ENC_DT = int(config['PINS']['RIGHT_ENC_DT'])

    # -------------------------------- actual test ------------------------------- #

    import time

    sampling_rate = 0.1 # read the encoder value once every 0.1 seconds
    sampling_time = 20 # read the encoder value for 10 seconds

    with Encoder(
        PIN_CLK=LEFT_ENC_CLK,
        PIN_DT=LEFT_ENC_DT
    ) as encoder:

        t_end = time.time() + sampling_time
        while time.time() < t_end:

            val = encoder.read_count()
            dir = encoder.read_direction()
            print('Encoder [{}] [{}]'.format(val, 'CCW' if dir == Direction.COUNTERCLOCKWISE else 'CW '))

            time.sleep(sampling_rate)
