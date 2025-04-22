import re

import tqdm
import netaddr

from .data import get_stream_bgp

DRY_RUN_COUNTER = 100_000


def load_cidr_by_asns(bgp_config, asns, dry_run=False):
    """
    BGPElem
    -------
    record_type|type|time|project|collector|router|router_ip|peer_asn|peer_address

    record_type: R RIB, U Update
    type: R RIB, A announcement, W withdrawal, S state message
    """
    asns_sets = {k: set(v) for k, v in asns.items()}
    result = {k: set() for k in asns}
    as_path_splitter = re.compile('[ ,]+')

    def _handle_elem(elem):
        if elem.record_type != 'rib':
            return
        if elem.type != 'R':
            return
        if 'as-path' not in elem.fields or 'prefix' not in elem.fields:
            return
        prefix = elem.fields['prefix']
        if prefix == '0.0.0.0/0' or prefix == '::/0':
            return

        try:
            last_asn = int(re.split(as_path_splitter, elem.fields['as-path'])[-1].strip('{}'))
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(elem.fields)
            print(f'error got asn {e}')
        else:
            for k, v in asns_sets.items():
                if last_asn in v:
                    # print(f'match: {elem.fields["prefix"]}')
                    result[k].add(prefix)

    # wrapper
    for i, elem in enumerate(tqdm.tqdm(
            get_stream_bgp(bgp_config['filepath']),
            ascii=True, desc='Filtering BGP Data', total=bgp_config['rough_size'],
        )):
        try:
            _handle_elem(elem)
        except KeyboardInterrupt:
            break

        if dry_run and i > DRY_RUN_COUNTER:
            break

    cidr_map = {}
    for k, v in result.items():
        print(f"merging {k}[{len(v)}] cidrs ...")
        merged = netaddr.cidr_merge(v)
        cidr_map[k] = [str(v.cidr) for v in merged]
    return cidr_map
