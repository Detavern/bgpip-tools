import os
import yaml
import logging
import datetime

__version__ = "0.1.0"

WORK_DIR = os.getcwd()
DATA_DIR = os.path.join(WORK_DIR, 'data')
CONFIG_DIR = os.path.join(WORK_DIR, 'config', 'stable')
DIST_DIR = os.path.join(WORK_DIR, 'dist')

BGP_V4_COLLECTOR = 'rrc00'
BGP_V6_COLLECTOR = 'route-views6'

_CONFIG_DICT = {}

DT_NOW = datetime.datetime.now(datetime.timezone.utc)

BOGONS_DATA = {
    'ipv4': {
        'filename': f'bogons_v4_{DT_NOW.strftime("%Y%m%d")}.txt',
        'url': 'https://team-cymru.org/Services/Bogons/fullbogons-ipv4.txt',
    },
    'ipv6': {
        'filename': f'bogons_v6_{DT_NOW.strftime("%Y%m%d")}.txt',
        'url': 'https://team-cymru.org/Services/Bogons/fullbogons-ipv6.txt',
    },
}

# logger
LOGGING_LEVEL = logging.INFO
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(LOGGING_LEVEL)

_CONSOLE_HANDLER = logging.StreamHandler()
_CONSOLE_HANDLER.setLevel(LOGGING_LEVEL)
_CONSOLE_HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s  %(levelname)s[%(name)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S'))

ROOT_LOGGER.addHandler(_CONSOLE_HANDLER)

logger = ROOT_LOGGER.getChild('config')


def load_config(config_dir=None):
    if config_dir is None:
        config_dir = CONFIG_DIR
    _CONFIG_DICT.clear()
    if os.path.isdir(config_dir) is False:
        raise FileNotFoundError(config_dir)
    
    logger.info(f'load configurations from {config_dir}')
    # load
    for filename in os.listdir(config_dir):
        if filename.startswith(('.', '#')):
            continue
        if filename.endswith(('.yml', '.yaml')):
            k = os.path.splitext(filename)[0]
            with open(os.path.join(config_dir, filename)) as f:
                v = yaml.safe_load(f)
            _CONFIG_DICT[k] = v


def get_config_dict():
    if not _CONFIG_DICT:
        load_config()
    return _CONFIG_DICT
