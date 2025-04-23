import re

from .config import get_config_dict
from .data import get_stream_asn


class ASNFilter:
    REGEX_IGNORECASE = True

    def __init__(self, country=None, regexp=None, jq=None):
        self.country = country
        self.regexp = regexp
        self.jq = jq

        self._regexp_pt = None
        if self.regexp:
            if self.REGEX_IGNORECASE:
                self._regexp_pt = re.compile(regexp, re.IGNORECASE)
            else:
                self._regexp_pt = re.compile(regexp)

    def match_dict(self, data: dict):
        if self.country:
            if self.country.startswith('!'):
                country = self.country[1:]
                if country == data['country']:
                    return False
            elif self.country != data['country']:
                return False
        
        if self.regexp:
            if not re.findall(self._regexp_pt, data['name']):
                return False

        return True


class ASNFilterGroup:
    """ASNFilterGroup

    A group of `ASNFilters` where the group matches if **any** individual filter matches.
    Operates in logical OR mode.
    """

    __filter_class__ = ASNFilter

    def __init__(self, *filters, includes: list=None, excludes: list=None):
        self.filters = filters
        self.includes = set(includes) if includes else set()
        self.excludes = set(excludes) if excludes else set()

    @classmethod
    def from_config(cls, config):
        filter_cls = cls.__filter_class__
        filters = []
        for cfg in config.pop('filters', []):
            filters.append(filter_cls(**cfg))
        return cls(*filters, **config)

    def match_self_asn(self, asn: int):
        if asn in self.excludes:
            return False
        if asn in self.includes:
            return True

    def match_dict(self, data: dict):
        asn_matched = self.match_self_asn(data['asn'])
        if asn_matched is not None:
            return asn_matched

        for filter_ in self.filters:
            if filter_.match_dict(data):
                return True
        return False


def load_asn_filters():
    asn_filter_dict = {}
    for k, v in get_config_dict().items():
        asn_filters = v.get('asn_filters')
        if not asn_filters:
            continue
        filter_group = ASNFilterGroup.from_config(asn_filters)
        asn_filter_dict[k] = filter_group
    return asn_filter_dict


def load_asns_by_config():
    asn_filter_dict = load_asn_filters()
    asns_dict = {}
    for name in asn_filter_dict:
        asns_dict[name] = []

    for asn_data in get_stream_asn():
        for name, filter_group in asn_filter_dict.items():
            if filter_group.match_dict(asn_data):
                asns_dict[name].append(asn_data['asn'])

    return asns_dict
