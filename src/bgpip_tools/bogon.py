import netaddr

from .data import get_bogon_data


def get_bogon_ipsets():
    ipsets = {}
    bogon_data = get_bogon_data()
    for k, bogons in bogon_data.items():
        ipset = netaddr.IPSet([netaddr.IPNetwork(cidr) for cidr in bogons])
        ipsets[k] = ipset
    return ipsets
