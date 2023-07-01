import RPi.GPIO as GPIO


class Counter:
    """
    Test class that serves as base for the 
    construction of the encoder.
    """

    def __init__(self, pin):

        self.pin = pin
        self._count = 0

        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, 
                              GPIO.FALLING, 
                              callback=self._increment_count, 
                              bouncetime=200)

    def _increment_count(self):
        self._count += 1

    def read(self):
        return self._count

    def close(self):
        GPIO.setup(self.pin, GPIO.IN)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            return False
        
        self.close()

        return True
    

if __name__ == '__main__':

    import time

    sampling_rate = 0.1  # read the counter value once every 0.1 seconds
    sampling_time = 20  # read the counter value for 20 seconds

    with Counter(
        pin=25
    ) as counter:
        
        t_end = time.time() + sampling_time
        while time.time() < t_end:

            val = counter.read_count()
            print(f'Counter values: {val}')

            time.sleep(sampling_rate)
