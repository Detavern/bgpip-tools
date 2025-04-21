import os
import json

from .config import DATA_DIR, dtnow
from .utils import download_asn_data


def prepare_data_asn():
    filename = f'asn_{dtnow.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    if os.path.isfile(filepath) is False:
        download_asn_data(DATA_DIR, filename)
    print(f"DATA[asninfo] found at {filepath}")


def stat_data_asn(filename=None):
    if filename is None:
        filename = f'asn_{dtnow.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    print(f"DATA[asninfo] load data at {filepath}")
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError(filepath)

    with open(filepath) as f:
        lines = sum(1 for _ in f)
    print(f'line counts: {lines}')


def get_stream_asn(filename=None):
    if filename is None:
        filename = f'asn_{dtnow.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    print(f"DATA[asninfo] load data at {filepath}")
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError(filepath)

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

