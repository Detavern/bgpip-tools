# BGPIP Tools

An IP address fetch tool based on `ASN` and `BGP` data.

The data acquisition logic is inspired by [china-operator-ip](https://github.com/gaoyifan/china-operator-ip).

## How to Getting the Data

The IP list (in CIDR format) is stored in the [ip-lists branch](https://github.com/Detavern/bgpip-tools/tree/ip-lists) of this repository,  
and is automatically updated daily via GitHub Actions.

## Data Sources

`BGP` routing data `RIB` snapshots (in `MRT` format) fetched via `bgpkit-broker`.
Currently:

- The `collector id` used for IPv4 is [`rrc00`](https://data.ris.ripe.net/)
- The `collector id` used for IPv6 is [`route-views6`](http://archive.routeviews.org/)

## Instructions

### Dependencies

- `wget`
- `python3`
- [asninfo](https://github.com/bgpkit/asninfo) (`cargo binstall asninfo`)
- [bgpkit](https://github.com/bgpkit/bgpkit-broker) (`cargo binstall bgpkit-broker@0.7.6`)
- [libbgpstream](https://bgpstream.caida.org/docs/install/bgpstream) (refer to the link for installation instructions)

### Installation

```bash
pip install .
# or pip install -e .
```

### Usage

```bash
bgpip-tools --help

Usage: bgpip-tools [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config-dir TEXT  Configuration directory
  --help                 Show this message and exit.

Commands:
  asn     ASN-related commands
  bgp     BGP-related commands
  bogon   Bogon network-related commands
  config  Configuration-related commands
```

#### Generate IP Network List

```bash
bgpip-tools bgp generate
```

## Acknowledgements

- Thanks to the original project and author [gaoyifan/china-operator-ip](https://github.com/gaoyifan/china-operator-ip)
- Thanks to the [RIPE RIS](https://data.ris.ripe.net/) project for providing BGP data sources
- Thanks to the [University of Oregon Route Views Archive Project](http://archive.routeviews.org) for BGP data sources
- Thanks to the [bgpkit](https://github.com/bgpkit/bgpkit-broker) project for related tools
- Thanks to the [bgpstream](https://bgpstream.caida.org) project for related tools
