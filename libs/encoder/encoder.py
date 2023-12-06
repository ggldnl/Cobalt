import RPi.GPIO as GPIO
import enum


class Direction(enum.Enum):
    STEADY = 0
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 2


class Encoder:

    def __init__(self, PIN_CLK, PIN_DT):

        self.PIN_CLK = PIN_CLK  # clock
        self.PIN_DT = PIN_DT  # data

        self._count = 0
        self._direction = Direction.STEADY

        self._current_clk = 0  # current clock value
        self._last_clk = 0  # last clock value

        self._setup()

    
    def _setup(self):
        """
        Sets up the hardware by setting the pins as INPUT.
        """

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # init the library

        GPIO.setup(self.PIN_CLK, GPIO.IN)
        GPIO.setup(self.PIN_DT, GPIO.IN)

        GPIO.add_event_detect(self.PIN_CLK, GPIO.FALLING, callback=self._update)
        #GPIO.add_event_detect(self.PIN_DT, GPIO.FALLING, callback=self._update)

    def _update(self):
        """
        Updates the encoder tick count every time an event is registered
        on the CLK pin.
        """

        self._current_clk = GPIO.input(self.PIN_CLK)

        if (
                self._current_clk != self._last_clk and
                self._current_clk == GPIO.HIGH
        ):

            self._count -= 1
            self._direction = Direction.COUNTERCLOCKWISE

        else:

            self._count += 1
            self._direction = Direction.CLOCKWISE
        
        self._last_clk = self._current_clk

    def reset(self):
        """
        Resets the number of encoder ticks.
        """
        self._count = 0

    def read_count(self):
        """
        Returns the number of encoder ticks measured so far.
        """
        return self._count

    def read_direction(self):
        """
        Returns the motion direction
        """
        return self._direction

    def close (self):
        """
        Frees the GPIO resources.
        """

        # calling GPIO.cleanup() will affect all the pins,
        # even the ones used in other modules
        # GPIO.cleanup()
        GPIO.setup(self.PIN_CLK, GPIO.IN)
        GPIO.setup(self.PIN_DT, GPIO.IN)

    def __enter__(self):
        return self

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            return False
        
        self.close()

        return True


if __name__ == '__main__':

    # -------------------------------- parameters -------------------------------- #

    LEFT_ENC_CLK = 25
    LEFT_ENC_DT = 8
    RIGHT_ENC_CLK = 23
    RIGHT_ENC_DT = 24

    # ----------------------------------- test ----------------------------------- #

    import time

    sampling_rate = 0.1  # read the encoder value once every 0.1 seconds
    sampling_time = 20  # read the encoder value for 10 seconds

    with Encoder(
        PIN_CLK=LEFT_ENC_CLK,
        PIN_DT=LEFT_ENC_DT
    ) as encoder:

        t_end = time.time() + sampling_time
        while time.time() < t_end:

            value = encoder.read_count()
            direction = encoder.read_direction()
            print('encoder [{}] [{}]'.format(
                value,
                'CCW' if direction == Direction.COUNTERCLOCKWISE else 'CW ')
            )

            time.sleep(sampling_rate)
