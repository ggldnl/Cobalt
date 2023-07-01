import RPi.GPIO as GPIO

class LED:
    """
    Simple class to control the behaviour of a LED.
    """

    def __init__(self, pin):

        self.pin = pin

        # state of the LED:
        # True if the LED is on
        # False if the LED is off
        self._state = False

        # set up the pin
        self._setup()

    def _setup(self):
        """
        Sets up the LED.
        """

        # GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)  # init the library
        GPIO.setup(self.pin, GPIO.OUT)  # set the pin as output

    def state(self):
        """
        Return the state of the LED.

        returns
        -------
            bool : True
                if the LED is turned on

            bool : False
                if the LED is turned off
        """
        return self._state

    def on(self):
        """
        Turns on the LED.
        """
        self._state = True
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        """
        Turns off the LED.
        """
        self._state = False
        GPIO.output(self.pin, GPIO.LOW)

    def flip(self):
        """
        Invert the state of the LED.
        """
        if self._state:
            self.off()
        else:
            self.on()

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
        GPIO.setup(self.pin, GPIO.IN)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
        return True


if __name__ == '__main__':

    import time

    sampling_rate = 1  # flip the LED once every second
    sampling_time = 20  # flip the LED for 20 seconds

    with LED(
        pin=25
    ) as led:
        
        t_end = time.time() + sampling_time
        while time.time() < t_end:

            state = led.state()
            print('Switching led from {} to {}'.format(
                'on' if state else 'off',
                'on' if not state else 'off'))
            led.flip()

            time.sleep(sampling_rate)
