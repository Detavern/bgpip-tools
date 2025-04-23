import os
import json

import pybgpstream

from .config import (
    DATA_DIR, BGP_V4_COLLECTOR, BGP_V6_COLLECTOR, BOGONS_DATA,
    DT_NOW, ROOT_LOGGER,
)
from .utils import download_asn_data, query_latest_bgp_data, download_remote_data

logger = ROOT_LOGGER.getChild('data')


def prepare_data_asn():
    filename = f'asn_{DT_NOW.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    if os.path.isfile(filepath) is False:
        download_asn_data(DATA_DIR, filename)
    logger.info(f"asn data found at {filepath}")


def stat_data_asn(filename=None):
    if filename is None:
        filename = f'asn_{DT_NOW.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    logger.info(f"loading asn data at {filepath}")
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError(filepath)

    with open(filepath) as f:
        lines = sum(1 for _ in f)
    logger.info(f"line counts: {lines}")


def get_stream_asn(filename=None):
    if filename is None:
        filename = f'asn_{DT_NOW.strftime("%Y%m%d")}.jsonl'
    filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
    logger.info(f"loading asn data at {filepath}")
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError(filepath)

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def prepare_data_bogons():
    for item in BOGONS_DATA.values():
        filename = item['filename']
        filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
        if os.path.isfile(filepath) is False:
            download_remote_data(item['url'], DATA_DIR, filename)
        logger.info(f"bogon data found at {filepath}")


def get_bogon_data():
    data = {}
    for k, v in BOGONS_DATA.items():
        data[k] = []
        filename = v['filename']
        filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
        if os.path.isfile(filepath) is False:
            raise FileNotFoundError(filepath)
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                data[k].append(line)
    return data


def get_bgp_info():
    info_mp = {
        'ipv4': query_latest_bgp_data(BGP_V4_COLLECTOR),
        'ipv6': query_latest_bgp_data(BGP_V6_COLLECTOR),
    }
    return info_mp


def prepare_data_bgp():
    res = {}
    for k, info in get_bgp_info().items():
        url = info['url']
        filename = os.path.basename(url)
        filepath = os.path.abspath(os.path.join(DATA_DIR, filename))
        if os.path.isfile(filepath) is False:
            download_remote_data(url, DATA_DIR, filename)
        logger.info(f"bgp data found at {filepath}")
        res[k] = {
            'collector': info['collector'],
            'data_dir': DATA_DIR,
            'filename': filename,
            'filepath': filepath,
            'rough_size': info['rough_size'],
        }
    return res


def get_stream_bgp(filepath):
    """Creates a generator that yields BGP elements from a given RIB (Routing Information Base) file.

    This function uses the pybgpstream library to read a BGP RIB file and iterate through its records.
    For valid records, it yields each BGP element contained within.

    likewise for `bgpreader -d singlefile -o rib-file=rib.gz -n 10`
    """
    stream = pybgpstream.BGPStream(data_interface='singlefile')
    stream.set_data_interface_option("singlefile", "rib-file", filepath)
    logger.info(f"loading bgp data at {filepath}")
    for rec in stream.records():
        if rec.status != "valid":
            raise ValueError(f"record in RIB file at {filepath} is not valid")

        # Each record contains multiple elements
        for elem in rec:
            yield elem
