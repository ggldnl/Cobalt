import logging

from Cobalt.hardlib.DRV8833.DRV8833 import DRV8833
from hardlib.VL53L0.VL53L0 import VL53L0
from Cobalt.hardlib.MPU6050.MPU6050 import MPU6050

from Cobalt.lib.Encoder.encoder import Encoder

# ---------------------------------- logging --------------------------------- #

import logging

# Formatter: A formatter defines the layout of the log records. 
# It determines how each message should be structured, including
# the timestamp, the severity level, the message itself, and any 
# additional data. You can use a built-in formatter or create 
# your own using Python's string formatting syntax.

# Handler: A handler specifies where the log records should be 
# sent. It can write them to a file, a socket, a database, or 
# any other type of output stream. You can configure a handler 
# to filter out messages based on their severity level, so that 
# only relevant ones are processed.

# Filter: A filter provides a way to further refine the messages 
# that are sent to a handler. It allows you to exclude certain 
# messages based on their content or other criteria.


# create a logger instance
logger = logging.getLogger('MAIN')
logger.setLevel(logging.DEBUG)

# create a formatter instance
formatter = logging.Formatter(
    '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'
    )

# create a handler instance
handler = logging.FileHandler('log/cobalt.log', 'w')
# handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)


# ----------------------------------- main ----------------------------------- #


def frange(start, stop=None, step=None):

    start = float(start)
    if stop is None:        # if stop is not specified
        stop = start + 0.0
        start = 0.0
    if step is None:        # if step is not specified
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


def main():

    # -------------------------------- parameters -------------------------------- #

    import configparser

    config = configparser.ConfigParser()
    config.read('config/config.ini')

    IN_1_LEFT = int(config['PINS']['IN_1_LEFT'])
    IN_2_LEFT = int(config['PINS']['IN_2_LEFT'])
    IN_1_RIGHT = int(config['PINS']['IN_1_RIGHT'])
    IN_2_RIGHT = int(config['PINS']['IN_2_RIGHT'])
    ENABLE = int(config['PINS']['ENABLE'])

    LEFT_ENC_CLK = int(config['PINS']['LEFT_ENC_CLK'])
    LEFT_ENC_DT = int(config['PINS']['LEFT_ENC_DT'])
    RIGHT_ENC_CLK = int(config['PINS']['RIGHT_ENC_CLK'])
    RIGHT_ENC_DT = int(config['PINS']['RIGHT_ENC_DT'])

    # ----------------------------------- main ----------------------------------- #

    from datetime import datetime
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logger.info('Starting Cobalt [{}]'.format(now_str))

    from lib.encoder import Encoder
    from hardlib.DRV8833.DRV8833 import DRV8833
    from lib.pid import PID

    with Encoder(
        PIN_CLK=LEFT_ENC_CLK,
        PIN_DT=LEFT_ENC_DT
    ) as left_encoder, Encoder(
        PIN_CLK=RIGHT_ENC_CLK,
        PIN_DT=RIGHT_ENC_DT
    ) as right_encoder, DRV8833(
        IN_1_A=IN_1_LEFT, IN_2_A=IN_2_LEFT,
        IN_1_B=None, IN_2_B=None,
        ENABLE=ENABLE
    ) as left_motor, DRV8833(
        IN_1_A=None, IN_2_A=None,
        IN_1_B=IN_1_RIGHT, IN_2_B=IN_2_RIGHT,
        ENABLE=ENABLE
    ) as right_motor:

        # motors
        target_speed = 1.0
        prev_left_speed = target_speed
        prev_right_speed = target_speed
        current_left_speed = prev_left_speed
        current_right_speed = prev_right_speed
        left_motor.write('a', current_left_speed)
        right_motor.write('b', current_right_speed)

        # PID
        left_motor_PID = PID(0.08, 0.01, 0.01)
        right_motor_PID = PID(0.08, 0.01, 0.01)

        conversion_factor = 260
        poles = 1

        def RPM2speed(current_RPM):
            """
            Given the current RPM, returns the current speed at which the motor is spinning
            based on the parameters of the motor (maximum RPM)

            Parameters
            ----------
            current_RPM: float
                current RPM value

            Returns
            -------
            the speed at which the motor is spinning
            """

            # we know from the manufacturer that at 6V the motor spins at 70 RPM (output shaft);
            # the conversion factor from the output shaft to the motor shaft is 260;
            max_RPM = 70

            # current_speed is in range [0, 1]
            # current_RPM : max_RPM = x : 100
            # x = (current_RPM * 100) / max_RPM
            x = (current_RPM * 100) / max_RPM

            return x / conversion_factor / poles

        PID_enabled = True

        # main loop
        import time
        sampling_rate = 0.5  # update once every 0.5 seconds
        sampling_time = 10  # run for 20 seconds
        t_end = time.time() + sampling_time
        while time.time() < t_end:

            # get encoder ticks
            left_encoder_val = left_encoder.read_count()  # encoder ticks in the sampling interval
            right_encoder_val = right_encoder.read_count()
            current_left_RPM = (left_encoder_val * 1 / sampling_rate * 60) / conversion_factor / poles
            current_right_RPM = (right_encoder_val * 1 / sampling_rate * 60) / conversion_factor / poles

            # compute the speed based on the RPM value and map it to the [0, 1] range
            current_left_speed = RPM2speed(current_left_RPM)
            current_right_speed = RPM2speed(current_right_RPM)

            if PID_enabled:

                # compute new speed
                prev_left_speed = current_left_speed
                current_left_speed = left_motor_PID.update(current_left_speed, target_speed)

                prev_right_speed = current_right_speed
                current_right_speed = right_motor_PID.update(current_right_speed, target_speed)

                left_motor.write('a', current_left_speed)
                right_motor.write('b', current_right_speed)

            # log the results
            result = 'Left ticks[{:5.2f}]\tRPM[{:5.2f}]\tprev_speed[{:5.2f}]\tcurr_speed[{:5.2f}]\t'        \
                     .format(left_encoder_val, current_left_RPM,  prev_left_speed, current_left_speed) +    \
                     'Right ticks[{:5.2f}]\tRPM[{:5.2f}]\tprev_speed[{:5.2f}]\tcurr_speed[{:5.2f}]\t'       \
                     .format(right_encoder_val, current_right_RPM, prev_right_speed, current_right_speed) + \
                     'err [{:5.2f}]'.format(abs(current_left_speed - current_right_speed))
            logger.debug(result)
            print(result)

            # reset the encoders and repeat the loop
            left_encoder.reset()
            right_encoder.reset()
            time.sleep(sampling_rate)

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logger.info('Exiting Cobalt [{}]'.format(now_str))


if __name__ == '__main__':
    main()
