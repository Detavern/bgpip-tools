import os
import yaml
import datetime

WORK_DIR = os.getcwd()
DATA_DIR = os.path.join(WORK_DIR, 'data')
CONFIG_DIR = os.path.join(WORK_DIR, 'config')
DIST_DIR = os.path.join(WORK_DIR, 'dist')
dtnow = datetime.datetime.now(datetime.timezone.utc)

_CONFIG_DICT = {}


def _load_config():
    _CONFIG_DICT.clear()
    if os.path.isdir(CONFIG_DIR) is False:
        raise FileNotFoundError(CONFIG_DIR)
    
    # load
    for filename in os.listdir(CONFIG_DIR):
        if filename.startswith(('.', '#')):
            continue
        if filename.endswith(('.yml', '.yaml')):
            k = os.path.splitext(filename)[0]
            with open(os.path.join(CONFIG_DIR, filename)) as f:
                v = yaml.safe_load(f)
            _CONFIG_DICT[k] = v


def get_config_dict():
    if not _CONFIG_DICT:
        _load_config()
    return _CONFIG_DICT
