import re

import tqdm
import netaddr

from .data import get_stream_bgp
from .bogon import get_bogon_ipset
from .config import ROOT_LOGGER

DRY_RUN_COUNTER = 100_000

logger = ROOT_LOGGER.getChild('bgp')


def load_cidr_by_asns(bgp_config, asns, v4=False, v6=False, dry_run=False):
    """Loading CIDRs from BGP snapshots by asns_filters

    BGPElem
    -------
    record_type|type|time|project|collector|router|router_ip|peer_asn|peer_address

    record_type: R RIB, U Update
    type: R RIB, A announcement, W withdrawal, S state message
    """
    asns_sets = {k: set(v) for k, v in asns.items()}
    result = {k: set() for k in asns}
    as_path_splitter = re.compile('[ ,]+')
    if not v4 and not v6:
        raise ValueError('either v4 or v6 should be True')

    def _handle_elem(elem):
        if elem.record_type != 'rib':
            return
        if elem.type != 'R':
            return
        if 'as-path' not in elem.fields or 'prefix' not in elem.fields:
            return
        prefix = elem.fields['prefix']
        is_v6_prefix = ':' in prefix
        if prefix == '0.0.0.0/0' or prefix == '::/0':
            return

        try:
            last_asn = int(re.split(as_path_splitter, elem.fields['as-path'])[-1].strip('{}'))
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f'parse asn error {e}, element: {elem}')
        else:
            for k, v in asns_sets.items():
                if last_asn in v:
                    if v4 and not is_v6_prefix:
                        result[k].add(prefix)
                    if v6 and is_v6_prefix:
                        result[k].add(prefix)

    # wrapper
    # TODO: require an estimated total size
    # total=estimated,
    for i, elem in enumerate(tqdm.tqdm(
            get_stream_bgp(bgp_config['filepath']),
            ascii=True, desc='Filtering BGP Data',
        )):
        try:
            _handle_elem(elem)
            if dry_run and i > DRY_RUN_COUNTER:
                break
        except KeyboardInterrupt:
            break

    # bogon filter
    bogon_ipset = get_bogon_ipset(v4, v6)
    def cidrs_filter(cidrs, ipset):
        for cidr in cidrs:
            if cidr not in ipset:
                yield cidr

    cidr_map = {}
    for k, cidrs in result.items():
        logger.info(f"merging {k}[{len(cidrs)}] cidrs ...")
        merged = netaddr.cidr_merge(cidrs_filter(cidrs, bogon_ipset))
        cidr_map[k] = [str(v.cidr) for v in merged]
    return cidr_map
