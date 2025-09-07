from argparse import ArgumentParser

import xml.etree.ElementTree as ET
from json import dumps as json_dumps

from plugins.translate.abstract import TranslatePluginRuleset, TranslatePluginStaticRoutes

# reads unencrypted OPNSense backup file and extracts its rules in CSV format

ALIASES = {}


def find_rec(node, element):
    for item in node.findall(element):
        yield item

        for child in find_rec(item, element):
            yield child


class OPNsenseRuleset(TranslatePluginRuleset):
    XML_ELEMENT_RULESET = 'filter'
    XML_ELEMENT_RULESET_NEW = 'OPNsense/Firewall/Filter/rules'
    XML_ELEMENT_ALIASES = 'OPNsense/Firewall/Alias/aliases'
    XML_ELEMENT_IF_GROUPS = 'ifgroups'
    XML_ELEMENT_NAT_SNAT = 'nat'
    XML_ELEMENT_NAT_SNAT_NEW = 'OPNsense/Firewall/Filter/snatrules'
    XML_ELEMENT_NAT_DNAT = 'nat/outbound'
    XML_ELEMENT_NAT_O2O_NEW = 'OPNsense/Firewall/Filter/onetoone'
    XML_ELEMENT_NAT_NPT_NEW = 'OPNsense/Firewall/Filter/npt'

    SEQ_ADD_NON_FLOAT = 10_000
    FIELDS_TYPING = {
        'quick': bool,
        'floating': bool,
        'interface': list,
        'protocol': list,
        # 'disabled': bool,
    }

    MAPPING = {
        'ipprotocol': {
            'inet46': [4, 6],
            'inet6': [6],
            'inet': [4],
        },
        'type': {
            'block': True,
            'reject': True,
            'pass': False,
        }
    }

    FIELDS_TRANSLATE = {
        'ipprotocol': 'proto_l3',
        'protocol': 'proto_l4',
        'type': 'block',
        'interface': 'interfaces',
    }
    FIELDS_SUB = ['source', 'destination']

    FIELDS_INFO = ['descr', 'category', 'uuid']
    FIELDS_SKIP = ['created', 'updated', 'statetype', 'log', 'source', 'destination']

    def __init__(self, raw: str):
        xml = ET.ElementTree(ET.fromstring(raw))
        self.ruleset = xml.getroot().find(self.XML_ELEMENT_RULESET)
        self.ruleset_new = xml.getroot().find(self.XML_ELEMENT_RULESET_NEW)

        self.aliases = xml.getroot().find(self.XML_ELEMENT_ALIASES)
        self.if_groups = xml.getroot().find(self.XML_ELEMENT_IF_GROUPS)
        self.nat_snat = xml.getroot().find(self.XML_ELEMENT_NAT_SNAT)  # todo: skip 'outbound'
        self.nat_snat_new = xml.getroot().find(self.XML_ELEMENT_NAT_SNAT_NEW)
        self.nat_dnat = xml.getroot().find(self.XML_ELEMENT_NAT_DNAT)
        # self.nat_dnat_new = xml.getroot().find(self.XML_ELEMENT_NAT_DNAT_NEW)
        self.nat_o2o_new = xml.getroot().find(self.XML_ELEMENT_NAT_O2O_NEW)
        self.nat_npt_new = xml.getroot().find(self.XML_ELEMENT_NAT_NPT_NEW)

        super().__init__({})

    def get(self) -> list[dict]:
        r = []
        i = 0

        for raw in self.raw['ruleset']:
            if 'uuid' not in raw.attrib:
                continue

            rule = {'info': {'uuid': raw.attrib['uuid']}}
            for cnf in raw:
                if cnf.tag in self.FIELDS_SKIP:
                    continue

                k = cnf.tag
                v = cnf.text
                if k in self.FIELDS_TYPING:
                    if self.FIELDS_TYPING[k] == bool:
                        v = v in ['yes', '1']

                    elif self.FIELDS_TYPING[k] == list and isinstance(v, str):
                        if v.find(',') != -1:
                            v = v.split(',')

                        elif v.find('/') != -1:
                            v = v.split('/')

                        else:
                            v = [v]

                if k == 'quick':
                    if not v:
                        raise ValueError(
                            "Non quick-mode rules are not yet supported! "
                            f"Rule: '{rule}' {cnf.text}"
                        )

                    continue

                if k in self.FIELDS_TRANSLATE:
                    k = self.FIELDS_TRANSLATE[k]

                if cnf.tag in self.MAPPING:
                    v = self.MAPPING[cnf.tag][v]

                elif isinstance(v, str):
                    v = v.strip()

                if cnf.tag in self.FIELDS_INFO:
                    rule['info'][k] = v

                else:
                    rule[k] = v

            if 'disabled' in rule and rule['disabled']:
                continue

            src = raw.find('source')
            if src is not None:
                for cnf in src:
                    v = cnf.text
                    if v in ALIASES:
                        v = ALIASES[v]

                    if cnf.tag == 'any':
                        continue

                    if cnf.tag == 'port':
                        rule['src_port'] = v

                    else:
                        rule['src'] = v

            rule['sequence'] = i
            if 'floating' in rule:
                if not rule['floating']:
                    rule['sequence'] += self.SEQ_ADD_NON_FLOAT

                rule.pop('floating')

            r.append(rule)
            i += 1

        r.append({'info': {'uuid': 'IMPLICIT DENY'}, 'block': True, 'sequence': 20_000})
        print('RULE COUNT:', len(r))

        return r


class OPNsenseRoutes(TranslatePluginStaticRoutes):
    XML_ELEMENT_ROUTES = 'staticroutes'
    XML_ELEMENT_GW = 'OPNsense/Gateways'


class OPNsenseInterfaces:
    XML_ELEMENT_INT = 'interfaces'
    XML_ELEMENT_VIP = 'virtualip'
