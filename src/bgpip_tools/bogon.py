import netaddr

from .data import get_bogon_data


def get_bogon_ipset(v4=True, v6=True):
    ipset = netaddr.IPSet()
    bogon_data = get_bogon_data()
    for k, bogons in bogon_data.items():
        if v4 and k == 'ipv4' or v6 and k == 'ipv6':
            [ipset.add(cidr) for cidr in bogons]
    return ipset


def get_bogon_ipsets():
    ipsets = {}
    bogon_data = get_bogon_data()
    for k, bogons in bogon_data.items():
        ipset = netaddr.IPSet([netaddr.IPNetwork(cidr) for cidr in bogons])
        ipsets[k] = ipset
    return ipsets
