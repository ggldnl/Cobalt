import RPi.GPIO as GPIO
import logging

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('DRV8833')
logger.setLevel(logging.DEBUG)

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
    This class represents a single dual H-bridge driver. It configures four pins
    for PWM output and can be used to control up to two DC motors bidirectionally
    at variable speed.

    You can declare IN_1_A and IN_2_A as None if you want to disable channel A
    and only keep channel B. The same holds for the other channel. If only one
    of the two pins for a channel is None while the other is not, an exception
    is raised.

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

    # e.g.
    # IN_1_A = 21, IN_2_A = 20
    # IN_1_B = 16, IN_2_B = 12
    # ENABLE = 7
    def __init__(self,
                 IN_1_A: int, IN_2_A: int,  # control pins for left motor
                 IN_1_B: int, IN_2_B: int,  # control pins for right motor
                 ENABLE: int,  # control pin to enable the board
                 decay: Decay = Decay.SLOW,  # decay mode
                 pwm_rate: int = 1000):  # frequency

        # check, for each pair of pins, if they are both None or both not None
        if (IN_1_A is None) ^ (IN_2_A is None):  # one of the two is None while the other is not
            error_msg = 'Invalid pin configuration: {}, {}'.format(IN_1_A, IN_2_A)
            logger.error(error_msg)
            raise ValueError(error_msg)

        if (IN_1_B is None) ^ (IN_2_B is None):  # one of the two is None while the other is not
            error_msg = 'Invalid pin configuration: {}, {}'.format(IN_1_B, IN_2_B)
            logger.error(error_msg)
            raise ValueError(error_msg)

        # pins are ok
        self.channel_A_enabled = True
        self.channel_B_enabled = True

        if IN_1_A is None and IN_2_A is None:
            self.channel_A_enabled = False

        if IN_1_B is None and IN_2_B is None:
            self.channel_B_enabled = False

        # pins
        self.IN_1_A = IN_1_A
        self.IN_2_A = IN_2_A
        self.IN_1_B = IN_1_B
        self.IN_2_B = IN_2_B
        self.ENABLE = ENABLE

        logger.debug('IN_1_A set to {}'.format(IN_1_A))
        logger.debug('IN_2_A set to {}'.format(IN_2_A))
        logger.debug('IN_1_B set to {}'.format(IN_1_B))
        logger.debug('IN_2_B set to {}'.format(IN_2_B))
        logger.debug('ENABLE set to {}'.format(ENABLE))

        # frequency
        self.pwm_rate = pwm_rate

        logger.debug('PWM frequency set to {}'.format(pwm_rate))

        # decay
        self.decay = decay

        logger.debug('Decay mode set to {}'.format(decay))

        # channel A and B rate
        self.channel_A_rate = 0  # pwm rate for channel A
        self.channel_B_rate = 0  # pwm rate for channel B

        self._setup()

    def _setup(self):
        """
        Sets up the hardware by setting the pins as OUTPUT
        and creating the pwm objects, one for each channel, with
        which the direction and speed of each channel is controlled.
        """

        logger.info('Starting hardware setup')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # init the library

        # TODO check if a None raises an exception
        GPIO.setup(self.IN_1_A, GPIO.OUT)
        GPIO.setup(self.IN_2_A, GPIO.OUT)
        GPIO.setup(self.IN_1_B, GPIO.OUT)
        GPIO.setup(self.IN_2_B, GPIO.OUT)
        GPIO.setup(self.ENABLE, GPIO.OUT)

        # enable the board pulling self.ENABLE HIGH
        # GPIO.output(self.ENABLE, GPIO.HIGH)
        # self.enable()

        # we could have multiple instasnces of the DRV8833
        # so we should first check if the enable pin is 
        # already in use
        if GPIO.gpio_function(18) != GPIO.OUT:
            self.enable()

        # create a PWM instance:
        # p = GPIO.PWM(channel, frequency)
        # TODO check if a None raises an exception
        self.pwm_1_A = GPIO.PWM(self.IN_1_A, self.pwm_rate)
        self.pwm_2_A = GPIO.PWM(self.IN_2_A, self.pwm_rate)
        self.pwm_1_B = GPIO.PWM(self.IN_1_B, self.pwm_rate)
        self.pwm_2_B = GPIO.PWM(self.IN_2_B, self.pwm_rate)

        self.pwm_1_A.start(0)
        self.pwm_2_A.start(0)
        self.pwm_1_B.start(0)
        self.pwm_2_B.start(0)

        logger.debug('Setup done')

    def _parse_channel(self, channel):
        """
        Used to validate user input. Check if the channel is valid.
        The channel can be specified using an integer (either 0 or 1)
        or a string ('a','b','A','B'). If these conditions aren't met
        an exception is raised.

        Parameters
        ----------
        channel: int/str
            input channel to check

        Returns
        -------
            if the input is a valid channel specifier, return its
            integer form:
                if channel == 'a'
                    return 0
                elif channel == 'b'
                    return 1.
        """

        # 65 is ascii uppercase a
        # 66 is ascii uppercase b
        # 97 is ascii lowercase a
        # 98 is ascii lowercase b

        if isinstance(channel, str):
            if channel.lower() == 'a':
                return 0
            elif channel.lower() == 'b':
                return 1

        if isinstance(channel, int):
            if channel == 0 or channel == 1:
                return channel

        # channel is not instance of int or string and is not 'a'/'b'/0/1

        error_msg = 'Invalid channel identifier: {}'.format(channel)
        logger.error(error_msg)
        raise ValueError(error_msg)

    def _parse_rate(self, rate):
        """
        Used to validate user input. Check if the rate is valid.
        PWM rate must be a float inside [-1.0, 1.0] range.
        Positive values are used to go forward;
        Zero is used to stop the channel;
        Negative values are used to go backward;

        Parameters
        ----------
        rate: float
            PWM rate, float in range [-1.0, 1.0]
        """

        if not isinstance(rate, (int, float)):
            error_msg = 'Invalid modulation rate: {}'.format(rate)
            logger.error(error_msg)
            raise ValueError(error_msg)

        return max(-1.0, min(1.0, rate))  # clip value

    def enable(self):
        """
        Enables the board.
        """
        logger.info('Board enabled')
        GPIO.output(self.ENABLE, GPIO.HIGH)

    def disable(self):
        """
        Disables the board.
        """
        logger.info('Board disabled')
        GPIO.output(self.ENABLE, GPIO.LOW)

    def getStatus(self):
        """
        Tells if the board is enabled or disabled.

        Returns
        -------
        status : boolean
            True if the board is enabled, False if the board is disabled
        """
        return GPIO.input(self.ENABLE)  # read the state

    def setDacayMode(self, decay):
        """
        Set the decay mode. The decay mode in a motor refers to the way in 
        which the current in the motor windings is reduced when the motor 
        is turned off.
        
        1. Fast decay mode (1): the current in the motor windings is rapidly 
            reduced to zero when the power supply is turned off. This causes 
            the motor to quickly come to a stop.

        2. Slow decay mode (0): the current in the motor windings is gradually 
            reduced to zero over a longer period of time. This can cause 
            the motor to continue rotating for a short period of time after 
            the power supply is turned off.
        
        Parameters
        ----------
        decay : Decay/str/int
            either SLOW or FAST if Decay
            either 'slow' or 'fast' if str
            either 0 or 1 if int
        """

        if not isinstance(decay, (Decay, str, int)):
            error_msg = 'Invalid decay specifier {} [class {}]'.format(decay, type(decay))
            logger.error(error_msg)
            raise ValueError(error_msg)

        # check if, being the correct type, the decay variable is a valid
        # decay string/integer
        if isinstance(decay, str) and (
                decay.lower() != 'slow' and
                decay.lower() != 'fast'
        ) or isinstance(decay, int) and (
                decay != 0 and
                decay != 1
        ):
            error_msg = 'Invalid decay mode: {}'.format(decay)
            logger.error(error_msg)
            raise ValueError(error_msg)

        # logging
        if isinstance(decay, Decay):
            decay_str = 'SLOW' if decay == Decay.SLOW else 'FAST'
        elif isinstance(decay, int):
            decay_str = 'SLOW' if decay == 0 else 'FAST'
        else:  # isinstance(decay, str)
            decay_str = decay.upper()
        logger.info('Decay mode set to: {}'.format(decay_str))

        self.decay = decay

    def setSlowDecay(self):
        """
        Set the decay mode to SLOW
        """
        logger.info('Decay mode set to: SLOW')
        self.decay = Decay.SLOW

    def setFastDecay(self):
        """
        Set the decay mode to FAST
        """
        logger.info('Decay mode set to: FAST')
        self.decay = Decay.FAST

    def getDecayMode(self):
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
        channel : int/str
            0/'a'/'A' for motor A, 1/'b'/'B' for motor B
        rate : float
            modulation value between -1.0 and 1.0, full reverse to full forward.
            0 stops the motor.
            
        Raises
        ------
        ValueError
            either if the channel identifier is invalid or the modulation rate 
            is out of bounds.
        """

        # check the channel
        parsed_channel = self._parse_channel(channel)

        # check the modulation rate
        parsed_rate = self._parse_rate(rate)

        # clip the rate value between -1.0 and 1.0
        # rate = round(rate, 2)
        # rate = max(-1.0, min(1.0, rate))

        # convert the rate (range [-1.0, 0.0]) into percentage and direction 
        # (rate >/< 0)
        # outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
        pwm = (abs(parsed_rate) * 100)
        logger.debug('Rate {0:.2f} converted to PWM value {1:5.2f}'.format(rate, pwm))

        if self.decay == Decay.SLOW:

            if parsed_channel == 0:
                if rate >= 0:  # forward
                    # dc is the duty cycle (0.0 <= dc <= 100.0)
                    self.pwm_1_A.ChangeDutyCycle(0)
                    self.pwm_2_A.ChangeDutyCycle(pwm)
                else:  # backward
                    self.pwm_1_A.ChangeDutyCycle(pwm)
                    self.pwm_2_A.ChangeDutyCycle(0)
                self.channel_A_rate = rate

            else:
                if rate >= 0:  # forward
                    self.pwm_1_B.ChangeDutyCycle(pwm)
                    self.pwm_2_B.ChangeDutyCycle(0)
                else:  # backward
                    self.pwm_1_B.ChangeDutyCycle(0)
                    self.pwm_2_B.ChangeDutyCycle(pwm)
                self.channel_B_rate = rate

        else:

            if parsed_channel == 0:
                if rate >= 0:  # forward
                    self.pwm_1_A.ChangeDutyCycle(100 - pwm)
                    self.pwm_2_A.ChangeDutyCycle(100)
                else:  # backward
                    self.pwm_1_A.ChangeDutyCycle(100)
                    self.pwm_2_A.ChangeDutyCycle(100 - pwm)
                self.channel_A_rate = rate

            else:
                if rate >= 0:  # forward
                    self.pwm_1_B.ChangeDutyCycle(100)
                    self.pwm_2_B.ChangeDutyCycle(100 - pwm)
                else:  # backward
                    self.pwm_1_B.ChangeDutyCycle(100 - pwm)
                    self.pwm_2_B.ChangeDutyCycle(100)
                self.channel_B_rate = rate

        direction = 'forward' if rate > 0 else 'backward'
        logger.info('Channel {0:s} {1:s} at {2:5.2f}%'.format(
            chr(parsed_channel + 65), direction, pwm))

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

        # check if the channel is correctly formatted and return the channel as int
        parsed_channel = self._parse_channel(channel)

        if parsed_channel == 0:
            return self.channel_A_rate

        return self.channel_B_rate

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
    def __del__(self):
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

    # ------------------------------- logger setup ------------------------------- #

    # create a logger instance
    logger = logging.getLogger('MAIN')
    logger.setLevel(logging.DEBUG)

    # create a formatter instance
    formatter = logging.Formatter(
        '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'
    )

    # create a handler instance
    handler = logging.FileHandler('../../log/DRV8833.log', 'w')
    # handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)


    # --------------------------- float range generator -------------------------- #

    # The Python range() works only with integers. It doesn’t support the 
    # float type:
    # Output TypeError: 'float' object cannot be interpreted as an integer
    # 
    # We can use Python generators and yield to write a custom function to 
    # generate a range of float numbers.
    def frange(start, stop=None, step=None):

        start = float(start)
        if stop is None:  # if stop is not specified
            stop = start + 0.0
            start = 0.0
        if step is None:  # if step is not specified
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


    # -------------------------------- actual test ------------------------------- #

    import configparser

    config = configparser.ConfigParser()
    config.read('../../config/config.ini')

    IN_1_LEFT = int(config['PINS']['IN_1_LEFT'])
    IN_2_LEFT = int(config['PINS']['IN_2_LEFT'])
    IN_1_RIGHT = int(config['PINS']['IN_1_RIGHT'])
    IN_2_RIGHT = int(config['PINS']['IN_2_RIGHT'])
    ENABLE = int(config['PINS']['ENABLE'])

    with DRV8833(
            IN_1_A=IN_1_LEFT, IN_2_A=IN_2_LEFT,
            IN_1_B=IN_1_RIGHT, IN_2_B=IN_2_RIGHT,
            ENABLE=7
    ) as motor_driver:

        motor_driver.setSlowDecay()
        print('Decay: {}'.format(
            'SLOW' if motor_driver.getDecayMode() == Decay.SLOW else 'FAST'
        ))

        for channel in range(2):

            for rate in frange(-1.0, 1.1, 0.1):
                print('Channel {}\tDirection {}\t Duty cycle {}'.format(
                    chr(channel + 65), 'forward' if rate > 0 else 'backward', round(rate, 2)))
                motor_driver.write(channel, rate)
                sleep(1)

            # stop the motor, otherwise the last suitable rate is kept
            print('Stopping channel {}'.format(chr(channel + 65)))
            motor_driver.write(channel, 0)

        # test both motors at the same time
        for rate in frange(-1.0, 1.0, 0.1):
            print('Both channels \tDirection {}\t Duty cycle {}'.format(
                'forward' if rate > 0 else 'backward', round(rate, 2)))
            motor_driver.write('a', rate)
            motor_driver.write('b', rate)
            sleep(1)

        # stop the motor, otherwise the last suitable rate is kept
        print('Stopping both channels')
        motor_driver.write('a', 0)
        motor_driver.write('b', 0)

    # the close() function is automatically called by __exit__()
    # once the with block ends
