from Cobalt.lib.PID.pid import PID
from Cobalt.lib.Encoder.encoder import Encoder
from Cobalt.hardlib.DRV8833.DRV8833 import DRV8833
import logging

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('MOTOR')
logger.setLevel(logging.DEBUG)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.DRV8833 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger

# ---------------------------- private constructor --------------------------- #

# from typing import Type, Any, TypeVar

# T = TypeVar("T")

# class NoPublicConstructor(type):
#     """
#     Metaclass that ensures a private constructor

#     If a class uses this metaclass like this:

#         class SomeClass(metaclass=NoPublicConstructor)
#             pass

#     If you try to instantiate your class ('SomeClass()'),
#     a 'TypeError' will be thrown.
#     """

#     def __call__(cls, *args, **kwargs):
#         raise TypeError(
#             f"{cls.__module__}.{cls.__qualname__} has no public constructor"
#         )

#     def _create(cls: Type[T], *args: Any, **kwargs: Any) -> T:
#         return super().__call__(*args, **kwargs)  # type: ignore


# class Point(metaclass=NoPublicConstructor):

#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

#     @classmethod
#     def from_cartesian(cls, x, y):
#         return cls._create(x, y)

#     @classmethod
#     def from_polar(cls, rho, phi):
#         return cls._create(rho * cos(phi), rho * sin(phi))

# Point(1, 2)  # raises a type error
# Point.from_cartesian(1, 2)  # OK
# Point.from_polar(1, 2)  # OK


# class Motor (metaclass=NoPublicConstructor):
#     def __init__(self, motor_driver : MotorDriver):
#         pass

# ---------------------------- motor core library ---------------------------- #

class Motor:
    """
        
    """

    def __init__ (self, DRV8833, channel):
        
        self.DRV8833 = DRV8833
        self.channel = channel



    def move (self, speed):

        speed = max(-1.0, min(1.0, speed)) # gives a number in range [-1.0, 1.0]
        self.DRV8833.write(self.channel, speed)

    
    def close (self):
        self.encoder.close()
        self.DRV8833.close()


    def __del__ (self):
        self.close()


    def __enter__ (self):
        pass


    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            #logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False
        
        self.close()

        return True


if __name__ == '__main__':

    with Motor (
        # motor pins
        IN_1_A = 21, IN_2_A = 20,
        IN_1_B = 16, IN_2_B = 12,
        ENABLE = 7,
        # encoder pins
        PIN_CLK = 25,
        PIN_DT = 8,
        # PID
        KP = 0.08,
        KI = 0.01,
        KD = 0.01
    ) as motor:
        pass        


# backward speed (0, 1)
# forward speed (0, 1)
# move speed (-1, 1)
# returns encoder
