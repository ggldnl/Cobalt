import logging
from lib.DRV8833.DRV8833 import DRV8833
from lib.VL53L0.VL53L0 import VL53L0
from lib.MPU6050.MPU6050 import MPU6050

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


def main():

    logger.info('Starting Cobalt')


    # TODO do something


    logger.info('Exiting Cobalt')

if __name__ == '__main__':
    main()