import RPi.GPIO as GPIO
import VL53L0X
import logging
import time

# ---------------------------------- logging --------------------------------- #

logger = logging.getLogger('VL53L0')
logger.setLevel(logging.INFO)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.VL53L0 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger

# ------------------------------ VL53L0 wrapper ------------------------------ #

class VL53L0:
    """
    This class makes it easy to initialize a sensor directly with a specific
    I2C address, to do readings with it and to log everything that happens
    during this process. 
    
    N.B. this does not implement any other timing process like periodically
    polling on the sensor.

    Remember to call the method close() before exiting the context and discarding
    the object to free the GPIO resources.

    ...

    Attributes
    ----------
    XSHUT : int
        pin used to enable/disable the board
    ADDR : int
        address to assign to the board

    Methods
    -------
    enable()
        enables the board.

    disable()
        disables the board.
    
    getStatus()
        tells if the board is enabled or disabled.
        
    read()
        returns the distance read by the sensor.

    close()
        frees the GPIO resources.
    """

    def __init__(self, 
                XSHUT,      # activation pin
                ADDR        # address
        ):

        self.XSHUT = XSHUT
        self.ADDR = ADDR

        self._setup()

    
    def _setup(self):
        """
        Sets up the hardware.
        """

        logger.info('Starting hardware setup')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # init the library

        # setup the GPIO to shut down the board
        GPIO.setup(self.XSHUT, GPIO.OUT)

        # turn off the board
        GPIO.output(self.XSHUT, GPIO.LOW)

        # keep the pin low for 1000 ms or so to make sure it resets
        time.sleep(1.0)

        # create a VL53L0X object

        self.tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
        self.tof.change_address(self.ADDR) # change address
        logger.debug('Address set to {}'.format(hex(self.ADDR).upper()))

        # enable the object
        GPIO.output(self.XSHUT, GPIO.HIGH)

        # open the object
        self.tof.open()

        # start ranging
        self.tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

        logger.info('Setup done')

    
    def enable (self):
        """
        Enables the board.
        """
        logger.info('Board enabled')
        GPIO.output(self.XSHUT, GPIO.HIGH)

    
    def disable (self):
        """
        Disables the board.
        """
        logger.info('Board disabled')
        GPIO.output(self.XSHUT, GPIO.LOW)

    
    def getStatus (self):
        """
        Tells if the board is enabled or disabled.

        Returns
        -------
        status : boolean
            True if the board is enabled, False if the board is disabled
        """
        return GPIO.input(self.XSHUT) # read the state

    # The __enter__ method is called when a block of code is entered, 
    # such as a with statement.
    def __enter__(self):
        return self
    

    def close(self):
        """
        Frees the GPIO resources.

        RPi.GPIO provides a built-in function GPIO.cleanup() to clean up 
        all the ports you’ve used. It resets any ports you have used in 
        the current program back to input mode. This prevents damage from
        a situation where you have a port set HIGH as an output and you 
        accidentally connect it to GND (LOW), which would short-circuit 
        the port and possibly fry it. Inputs can handle either 0V (LOW) 
        or 3.3V (HIGH), so it’s safer to leave ports as inputs.
        If you don't do this, any ports which are in use at the time of 
        an error or Keyboard Interrupt will stay set exactly as they were, 
        even after the program exits.
        """
        logger.info('GPIO cleanup')
        
        # stop ranging
        self.tof.stop_ranging()
        
        # stop I2C communication
        self.tof.close()

        # calling GPIO.cleanup() will affect all the pins,
        # even the ones used in other modules
        # GPIO.cleanup()
        GPIO.setup(self.XSHUT, GPIO.IN)


    # The __exit__ method is called when the block of code is exited, 
    # either normally or due to an exception being raised.
    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True

    
#    def startRanging(self):
#        logger.info('Start ranging')
#        self.tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
#
#
#    def stopRanging(self):
#        logger.info('Stop ranging')
#        self.tof.stop_ranging()


    def read (self):
        """
        Read the distance from the sensor.

        Returns
        -------
        distance : float
            distance from the sensor
        """

        distance = self.tof.get_distance()
        if distance < 0.0:
            distance = 0.0
                
        logger.debug('Distance read: {}'.format(round(distance, 2)))
            
        return distance
        

if __name__ == '__main__':

    import time

    xshut = [18, 26, 6]
    addr  = [0x2B, 0x2C, 0x2D]

    with VL53L0X(xshut[0], addr[0]) as tof:

        interval = 30 # seconds
        t_end = time.time() + interval

        while time.time() < t_end:

            distance = tof.read()
            print('Sensor[{}] read distance {}'.format(tof.ADDR, distance))

