import logging
import smbus

# ---------------------------------- logging --------------------------------- #

# create a logger instance
logger = logging.getLogger('MPU6050')
logger.setLevel(logging.INFO)

# done this way bot to omit the FileHandler specification and to avoid
# the logger to write MAIN.MPU6050 on the file. For some reason this
# works
parent_logger = logging.getLogger('MAIN')
logger.parent = parent_logger


# --------------------------- MPU6050 core library --------------------------- #

class MPU6050:
    """
    This class represents a MPU6050 

    N.B. this does not implement any other timing process.

    ...
    
    Methods
    -------
    read()
        reads accelerometer, gyroscope and temperature data
    """


    def __init__ (self):

        # pins
        self.PWR_MGMT_1   = 0x6B
        self.SMPLRT_DIV   = 0x19
        self.CONFIG       = 0x1A
        self.GYRO_CONFIG  = 0x1B
        self.INT_ENABLE   = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H  = 0x43
        self.GYRO_YOUT_H  = 0x45
        self.GYRO_ZOUT_H  = 0x47
        self.TEMP_H       = 0x41

        # I2C communication
        self.bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
        self.device_address = 0x68   # MPU6050 device address

        self._setup()


    def _setup (self):
        """
        Sets up the hardware.
        """

        logger.info('Starting hardware setup')

        # write to sample rate register
        self.bus.write_byte_data(self.device_address, self.SMPLRT_DIV, 7)

        # write to power management register
        self.bus.write_byte_data(self.device_address, self.PWR_MGMT_1, 1)

        # write to configuration register
        self.bus.write_byte_data(self.device_address, self.CONFIG, 0)

        # write to Gyro configuration register
        self.bus.write_byte_data(self.device_address, self.GYRO_CONFIG, 24)

        # write to interrupt enable register
        self.bus.write_byte_data(self.device_address, self.INT_ENABLE, 1)

        logger.info('Setup done')


    def _read_raw_data(self, addr):
        """
        Read the raw data from the registers (high and low).

        Parameters
        ----------
        addr : int
            address from which to read
        """
        
        # accelero and gyro value are 16-bit
        high = self.bus.read_byte_data(self.device_address, addr)
        low = self.bus.read_byte_data(self.device_address, addr+1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536

        logger.debug('Data read: {}'.format(value))

        return value


    def read (self):
        """
        Reads accelerometer, gyroscope and temperature data.

        Returns
        -------
            tuple containing:
                acceleration along x axis
                acceleration along y axis
                acceleration along z axis
                angular velocity along x axis
                angular velocity along y axis
                angular velocity along z axis
                temperature
        """

        logger.info('Reading data')

        # read accelerometer raw value
        acc_x = self._read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self._read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self._read_raw_data(self.ACCEL_ZOUT_H)

        # read gyroscope raw value
        gyro_x = self._read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self._read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self._read_raw_data(self.GYRO_ZOUT_H)

        # read temperature raw value
        temp = self._read_raw_data(self.TEMP_H)

        # full scale range +/- 250 degree/C as per sensitivity scale factor

        # acceleration along the X axis = (accelerometer X axis raw data/16384) g.
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0

        # angular velocity along the X axis = (gyroscope X axis raw data/131) °/s.
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0

        # temperature in degrees C = ((temperature sensor data)/340 + 36.53) °/c.
        T = temp/340.0 + 36.53

        return (Ax, Ay, Az, Gx, Gy, Gz, T)


    # The __enter__ method is called when a block of code is entered, 
    # such as a with statement.
    def __enter__ (self):
        pass


    # The __exit__ method is called when the block of code is exited, 
    # either normally or due to an exception being raised.
    def __exit__(self, exc_type, exc_value, tb):

        if exc_type is not None:
            logger.error('Exception during call to __exit__: {}'.format(exc_type))
            return False

        return True

# ----------------------------------- main ----------------------------------- #

if __name__ == '__main__':

    with MPU6050() as mpu:

        import time
        interval = 30 # seconds
        t_end = time.time() + interval

        while time.time() < t_end:

            Ax, Ay, Az, Gx, Gy, Gz, T = mpu.read()
            print('Ax[{}]\tAy[{}]\tAz[{}]\tGx[{}]\tGy[{}]\tGz[{}]\tT[{}]' \
                .format(Ax, Ay, Az, Gx, Gy, Gz, T))
