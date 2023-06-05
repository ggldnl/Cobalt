import configparser

class Cobalt:
    """
    Main class
    """

    def __init__ (self):

        # read the configuration file to retrieve the parameters
        config = configparser.ConfigParser()
        config.read('../config/config.ini')

        LEFT_1  = config['PINS']['LEFT_1']
        LEFT_2  = config['PINS']['LEFT_2']
        RIGHT_1 = config['PINS']['RIGHT_1']
        RIGHT_2 = config['PINS']['RIGHT_2']
        ENABLE  = config['PINS']['ENABLE']

        LEFT_ENC_CLK  = config['PINS']['LEFT_ENC_CLK']
        LEFT_ENC_DT   = config['PINS']['LEFT_ENC_DT']
        RIGHT_ENC_CLK = config['PINS']['RIGHT_ENC_CLK']
        RIGHT_ENC_DT  = config['PINS']['RIGHT_ENC_DT']

        self.left_motor = None
        self.right_motor = None

        # launch the background updater thread
        # TODO thread

    
    def forward (self, distance, speed):
        # TODO how much? at what speed?    
        self.left_motor.forward()
        self.right_motor.forward()


    def backward (self, distance, speed):
        # TODO how much? at what speed?
        self.left_motor.backward()
        self.right_motor.backward()


    def rotate_clockwise (self, angle, speed):
        # TODO how much? at what speed?
        self.left_motor.forward()
        self.right_motor.backward()


    def rotate_counter_clockwise (self, angle, speed):
        # TODO how much? at what speed?
        self.left_motor.backward()
        self.right_motor.forward()


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
        # logger.info('GPIO cleanup')

        self.left_motor.close()
        self.right_motor.close()
   

    # When an object is no longer being used by a program, Python's garbage 
    # collector automatically deletes the object and frees up the memory it 
    # was using. Before the object is deleted, however, Python calls its 
    # __del__ method (if it has one) to perform any necessary cleanup actions.
    def __del__ (self):
        # self.close()
        pass


    def __enter__(self):
        return self


    # The __exit__ method is called when the block of code is exited, 
    # either normally or due to an exception being raised.
    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            # TODO
            # logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True


if __name__ == '__main__':

    import time
    with Cobalt () as cobalt:

        """
        # make a square
        for _ in range(4):

            cobalt.forward(distance = 50, speed = 50)
            cobalt.rotate_clockwise(angle = 90, speed = 50)
            time.sleep(1)
        
        # make a circle
        # TODO
        """
        
        msg = ''
        while msg.lower() != 'exit':

            cobalt.forward(distance=50, speed=50)
            
            msg = input()

            try:
                p, i, d = msg.split(' ')

                cobalt.left_motor.pid.set_parameters(p, i, d)
                cobalt.right_motor.pid.set_parameters(p, i, d)
            except:
                pass