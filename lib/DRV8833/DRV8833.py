import RPi.GPIO as GPIO
import logging

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('DRV8833')
logger.setLevel(logging.INFO)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.DRV8833 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger


# --------------------------- DRV8833 core library --------------------------- #


import enum

class Decay(enum.Enum):
    FAST = 0
    SLOW = 1


class DRV8833:
    """
    This class represents a single dual H-bridge driver.  It configures four pins
    for PWM output and can be used to control two DC motors bidirectionally
    at variable speed.

    N.B. this does not implement any other timing process, it simply sets
    motor PWM levels but does not apply feedback, duration, or trajectory.

    Remember to call the method close() before exiting the context and discarding
    the object to free the GPIO resources.

    ...

    Attributes
    ----------
    IN_1_A : int
        pin used to control channel A input 1 of the DRV8833 board
    IN_2_A : int
        pin used to control channel A input 2 of the DRV8833 board
    IN_1_B : int
        pin used to control channel B input 1 of the DRV8833 board
    IN_2_B : int
        pin used to control channel B input 2 of the DRV8833 board
    ENABLE : int
        pin used to enable/disable the board
        
    Methods
    -------
    enable()
        enables the board.

    disable()
        disables the board.
    
    getStatus()
        tells if the board is enabled or disabled.

    write(channel, rate)
        sets the speed and direction (rate) on a single motor channel.
        
    read(channel)
        returns the speed and direction (rate) of the specified motor channel.

    setDacayMode(decay)
        set the decay mode.
    
    setSlowDecay()
        set the current decay mode to SLOW.

    setFastDecay()
        set the current decay mode to FAST.
    
    getDecayMode()
        returns the current decay mode.

    close()
        frees the GPIO resources.
    """

    def __init__(self,
                IN_1_A = 21, IN_2_A = 20,   # control pins for left motor
                IN_1_B = 16, IN_2_B = 12,   # control pins for right motor
                ENABLE = 7,
                pwm_rate=1000):             # frequency

        # pins
        self.IN_1_A = IN_1_A
        self.IN_2_A = IN_2_A
        self.IN_1_B = IN_1_B
        self.IN_2_B = IN_2_B
        self.ENABLE = ENABLE
        
        # frequency
        self.pwm_rate = pwm_rate

        # decay
        self.decay = Decay.SLOW

        self._setup()


    def _setup(self):
        """
        Sets up the hardware by setting the pins as OUTPUT
        and creating the pwm objects, one for each channel, whith
        which the direction and speed of each channel is controlled.
        """

        logger.info('Starting hardware setup')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # init the library

        GPIO.setup(self.IN_1_A, GPIO.OUT)
        GPIO.setup(self.IN_2_A, GPIO.OUT)
        GPIO.setup(self.IN_1_B, GPIO.OUT)
        GPIO.setup(self.IN_2_B, GPIO.OUT)
        GPIO.setup(self.ENABLE, GPIO.OUT)

        # enable the board pulling self.ENABLE HIGH
        GPIO.output(self.ENABLE, GPIO.HIGH)

        # create a PWM instance:
        # p = GPIO.PWM(channel, frequency)
        self.pwm_1_A = GPIO.PWM(self.IN_1_A, self.pwm_rate)
        self.pwm_2_A = GPIO.PWM(self.IN_2_A, self.pwm_rate)
        self.pwm_1_B = GPIO.PWM(self.IN_1_B, self.pwm_rate)
        self.pwm_2_B = GPIO.PWM(self.IN_2_B, self.pwm_rate)

        self.pwm_1_A.start(0)
        self.pwm_2_A.start(0)
        self.pwm_1_B.start(0)
        self.pwm_2_B.start(0)

        logger.info('Setup done')

    
    def enable (self):
        """
        Enables the board.
        """
        logger.info('Board enabled')
        GPIO.output(self.ENABLE, GPIO.HIGH)

    
    def disable (self):
        """
        Disables the board.
        """
        logger.info('Board disabled')
        GPIO.output(self.ENABLE, GPIO.LOW)

    
    def getStatus (self):
        """
        Tells if the board is enabled or disabled.

        Returns
        -------
        status : boolean
            True if the board is enabled, False if the board is disabled
        """
        return GPIO.input(self.ENABLE) # read the state


    def setDacayMode (self, decay):
        """
        Set the decay mode. The decay mode in a motor refers to the way in 
        which the current in the motor windings is reduced when the motor 
        is turned off.
        
        1. Fast decay mode: the current in the motor windings is rapidly 
            reduced to zero when the power supply is turned off. This causes 
            the motor to quickly come to a stop.

        2. Slow decay mode: the current in the motor windings is gradually 
            reduced to zero over a longer period of time. This can cause 
            the motor to continue rotating for a short period of time after 
            the power supply is turned off.
        
        Parameters
        ----------
        decay : Decay
            either LOW or FAST
        """

        logger.info('Decay mode set to: {}'.format(decay))
        self.decay = decay


    def setSlowDecay (self):
        """
        Set the decay mode to SLOW
        """
        logger.info('Decay mode set to: SLOW')
        self.decay = Decay.SLOW

    
    def setFastDecay (self):
        """
        Set the decay mode to FAST
        """
        logger.info('Decay mode set to: FAST')
        self.decay = Decay.FAST

    
    def getDecayMode (self):
        """
        Get the current decay mode.

        Returns
        -------
        decay : Decay
            the current decay mode.
        """
        return self.decay


    def write(self, channel, rate):
        """
        Set the speed and direction on a single motor channel. The speed and
        direction for each channel is set according to the following tables:

        +------+------+-------------------------+
        | xIN1 | xIN2 |        FUNCTION         |
        +------+------+-------------------------+
        | PWM  | 0    | Forward PWM, fast decay |
        | 1    | PWM  | Forward PWM, slow decay |
        | 0    | PWM  | Reverse PWM, fast decay |
        | PWM  | 1    | Reverse PWM, slow decay |
        +------+------+-------------------------+

        +------+------+-------------------------+
        | xIN1 | xIN2 |       FAST DECAY        |
        +------+------+-------------------------+
        | PWM  | 0    | Forward PWM, fast decay |
        | 0    | PWM  | Reverse PWM, fast decay |
        +------+------+-------------------------+

        +------+------+-------------------------+
        | xIN1 | xIN2 |       SLOW DECAY        |
        +------+------+-------------------------+
        | 1    | PWM  | Forward PWM, slow decay |
        | PWM  | 1    | Reverse PWM, slow decay |
        +------+------+-------------------------+

        Parameters
        ----------
        channel : int
            0 for motor A, 1 for motor B
        reate : float
            modulation value between -1.0 and 1.0, full reverse to full forward.
            
        Raises
        ------
        ValueError
            either if the channel identifier is invalid or the modulation rate 
            is out of bounds.
        """

        rate = round(rate, 2)

        if (
            channel != 0 and 
            channel != 'A' and
            channel != 1 and
            channel != 'B'
        ):
            error_msg = 'Invalid channel identifier: {}'.format(channel)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if rate < -1.0 or rate > 1.0:
            error_msg = 'Invalid modulation rate: {}'.format(rate)
            logger.error(error_msg)
            raise ValueError(error_msg)

        # convert the rate (range [-1.0, 0.0]) into percentage and direction 
        # (rate >/< 0)
        # outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
        pwm = (abs(rate) * 100)
        logger.debug('Rate {} converted to PWM value {}'.format(rate, pwm))

        if self.decay == Decay.FAST:

            if channel == 0 or channel == 'A' or channel == 'a':
                if rate > 0: # forward
                    # dc is the duty cycle (0.0 <= dc <= 100.0)
                    self.pwm_1_A.ChangeDutyCycle(0)
                    self.pwm_2_A.ChangeDutyCycle(pwm)    
                elif rate < 0: # backward
                    self.pwm_1_A.ChangeDutyCycle(pwm)
                    self.pwm_2_A.ChangeDutyCycle(0)

            elif channel == 1 or channel == 'B' or channel == 'b':
                if rate > 0: # forward
                    self.pwm_1_B.ChangeDutyCycle(pwm)
                    self.pwm_2_B.ChangeDutyCycle(0)
                elif rate < 0: # backward
                    self.pwm_1_B.ChangeDutyCycle(0)
                    self.pwm_2_B.ChangeDutyCycle(pwm)

        elif self.decay == Decay.SLOW:

            if channel == 0 or channel == 'A' or channel == 'a':
                if rate > 0: # forward
                    self.pwm_1_A.ChangeDutyCycle(pwm)
                    self.pwm_2_A.ChangeDutyCycle(100)                
                elif rate < 0: # backward
                    self.pwm_1_A.ChangeDutyCycle(100)
                    self.pwm_2_A.ChangeDutyCycle(pwm)

            elif channel == 1 or channel == 'B' or channel == 'b':
                if rate > 0: # forward
                    self.pwm_1_B.ChangeDutyCycle(100)
                    self.pwm_2_B.ChangeDutyCycle(pwm)
                elif rate < 0: # backward
                    self.pwm_1_B.ChangeDutyCycle(pwm)
                    self.pwm_2_B.ChangeDutyCycle(100)

        logger.info('Channel {} {} at {}%'.format(
            channel, 'forward' if rate > 0 else 'backward', pwm))
                

    def read(self, channel):
        """
        Read the speed and direction on a single motor channel.

        Parameters
        ----------
        channel : int
            0 for motor A, 1 for motor B
        
        Returns
        -------
        rate : float
            the modulation rate for that channel

        Raises
        ------
        ValueError
            if the channel parameter is not a valid channel identifier.

        """

        if channel == 0 or channel == 'A' or channel == 'a':
            return self.channel_A_rate
        elif channel == 1 or channel == 'B' or channel == 'b':
            return self.channel_B_rate
        error_msg = 'Invalid channel identifier: {}'.format(channel)
        logger.error(error_msg)
        raise ValueError(error_msg)


    # The __enter__ method is called when a block of code is entered, 
    # such as a with statement.
    def __enter__(self):
        return self
    

    def close (self):
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

        # calling GPIO.cleanup() will affect all the pins,
        # even the ones used in other modules
        # GPIO.cleanup()
        GPIO.setup(self.IN_1_A, GPIO.IN)
        GPIO.setup(self.IN_1_B, GPIO.IN)
        GPIO.setup(self.IN_2_A, GPIO.IN)
        GPIO.setup(self.IN_2_B, GPIO.IN)
        GPIO.setup(self.ENABLE, GPIO.IN)
   

    # When an object is no longer being used by a program, Python's garbage 
    # collector automatically deletes the object and frees up the memory it 
    # was using. Before the object is deleted, however, Python calls its 
    # __del__ method (if it has one) to perform any necessary cleanup actions.
    def __del__ (self):
        # self.close()
        pass


    # The __exit__ method is called when the block of code is exited, 
    # either normally or due to an exception being raised.
    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True


# ----------------------------------- main ----------------------------------- #


if __name__ == '__main__':

    from time import sleep

    # The Python range() works only with integers. It doesn’t support the 
    # float type:
    # Output TypeError: 'float' object cannot be interpreted as an integer
    # 
    # We can use Python generators and yield to write a custom function to 
    # generate a range of float numbers.
    def frange(start, stop=None, step=None):

        start = float(start)
        if stop == None:        # if stop is not specified
            stop = start + 0.0
            start = 0.0
        if step == None:        # if step is not specified
            step = 1.0

        # print("start = ", start, "stop = ", stop, "step = ", step)

        count = 0
        while True:
            temp = float(start + count * step)
            if step > 0 and temp >= stop:
                break
            elif step < 0 and temp <= stop:
                break
            yield temp
            count += 1


    with DRV8833() as motor_driver:

        # channel = 'A'
        # motor_driver.write(channel, 1.0)
        # motor_driver.write(channel, -1.0)
        # sleep(5)

        channel = 'A'
        for rate in frange(-1.0, 1.0, 0.1):
            print('Channel {}\tDirection {}\t Duty cycle {}'.format(
                channel, 'forward' if rate > 0 else 'backward' ,rate))
            motor_driver.write(channel, rate)
            sleep(1)

        # the close() function is automatically called by __exit__()
        # once the with block ends