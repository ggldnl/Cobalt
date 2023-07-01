import os


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'config.ini')
LOG_PATH = os.path.join(ROOT_DIR, 'log', 'cobalt.log')