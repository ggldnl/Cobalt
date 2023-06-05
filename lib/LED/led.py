import RPi.GPIO as GPIO

class LED:
    """
    LED control
    """

    def __init__ (self, PIN):

        self.PIN = PIN
        self._state = False

        self._setup()

    def _setup (self):

        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM) # init the library
        GPIO.setup(self.PIN, GPIO.OUT)

    def state (self):
        return self._state

    def on (self):
        self._state = True
        GPIO.output(self.PIN, GPIO.HIGH)

    def off (self):
        self._state = False
        GPIO.output(self.PIN, GPIO.LOW)

    def flip (self):
        if self._state:
            self.off()
        else:
            self.on()

    def close(self):
        GPIO.setup(self.PIN, GPIO.IN)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
        return True

if __name__ == '__main__':

    import time

    sampling_rate = 1 # flip the led once every second
    sampling_time = 20 # flip the led for 20 seconds

    with LED(
        PIN = 25
    ) as led:
        
        t_end = time.time() + sampling_time
        while time.time() < t_end:

            state = led.state()
            print('Switching led from {} to {}'.format(
                'on' if state else 'off',
                'on' if not state else 'off'))
            led.flip()

            time.sleep(sampling_rate)
