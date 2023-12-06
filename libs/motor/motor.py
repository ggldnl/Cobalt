from ..PID.pid import PID


class Motor:

    def __init__(self):

        # hardware components
        self.motor_driver = None
        self.encoder = None
        self.PID = PID(
            KP=0.08,
            KI=0.01,
            KD=0.01
        )

        self.last_update = 0
        self.current_speed = 0

    def update(self, target_speed):
        """
        Updates the state of the motor.
        The motor block needs to be used inside an update loop.
        We assign a target speed that we want the motor to reach and
        we periodically update the motor to perform the necessary
        corrections in order to go as close as possible to it.

        Pseudocode:

            get encoder ticks

            compute speed from encoder ticks in the time frame
                (current_update - last_update)

            now we have the current_speed and the target_speed

            use the PID controller to compute the correction
                for the current_speed
        """

        ticks = self.encoder.read_count()
        speed = ticks / (now() - self.last_update)  # m/s
        self.current_speed = self.PID.update(speed, target_speed)

        # apply the correction
        # self.motor_driver.write()
        print(f'new speed: {self.current_speed}')

    def close(self):
        """
        Frees the GPIO resources.
        """
        self.motor_driver.close()
        self.encoder.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            return False
        
        self.close()

        return True


if __name__ == '__main__':

    print('hello')