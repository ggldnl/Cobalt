import logging

from hardware_lib.DRV8833.DRV8833 import DRV8833
from hardware_lib.VL53L0.VL53L0 import VL53L0
from hardware_lib.MPU6050.MPU6050 import MPU6050

from lib.encoder import Encoder
#from test.counter import Counter


# ---------------------------------- logging --------------------------------- #

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
logger.setLevel(logging.INFO)

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
    if stop == None:        # if stop is not specified
        stop = start + 0.0
        start = 0.0
    if step == None:        # if step is not specified
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

    logger.info('Starting Cobalt')

    import time

    #with Encoder(
    #    PIN_A = 25,
    #    PIN_B = 8
    #) as encoder, Counter(
    #    25
    #) as counter, DRV8833(
    #    IN_1_A = 21, IN_2_A = 20,
    #    IN_1_B = 16, IN_2_B = 12,
    #    ENABLE = 7
    #) as motor_driver:

    with Encoder(
        PIN_CLK = 25,
        PIN_DT = 8
    ) as encoder, DRV8833(
        IN_1_A = 21, IN_2_A = 20,
        IN_1_B = 16, IN_2_B = 12,
        ENABLE = 7
    ) as motor_driver:

        channel = 'A'
        for rate in frange(-1.0, 1.0, 0.1):
            print('Channel {}\tDirection {}\t Duty cycle {}'.format(
                channel, 'forward' if rate > 0 else 'backward' , round(rate, 2)))
            motor_driver.write(channel, rate)

            val = encoder.read_count()
            #val = counter.get_value()
            print('Encoder ticks: {}'.format(val))

            time.sleep(1)

        # stop the motor, otherwise the last suitable rate is kept
        print('Stopping channel {}'.format(channel))
        motor_driver.write(channel, 0)



    logger.info('Exiting Cobalt')

if __name__ == '__main__':
    main()