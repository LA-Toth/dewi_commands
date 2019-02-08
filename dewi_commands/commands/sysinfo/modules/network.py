# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import re
import subprocess

from dewi_module_framework.module import Level
from dewi_utils.network import NetworkCardVendors
from ..common.base_module_ import BaseModule


class NetworkModule(BaseModule):
    PREFIXES = ['en', 'eth']

    def provide(self):
        return 'network'

    def run(self):

        vendors = set()
        self._process(vendors)

        for vendor in vendors:
            self.add_message(Level.INFO, 'Network', 'Interfaces', 'Network card vendor: ' + vendor)

    def _process(self, vendors: set):

        content = subprocess.check_output('ifconfig').decode('UTF-8')

        oui = self._ll_node.oui
        iface_name = ''
        for line in content.splitlines():
            m = re.match(r'^([a-z0-9]+): .*', line)
            if m:
                iface_name = m.group(1)
            elif 'ether' in line:
                m = re.match(r'.*ether ([^ ]+).*', line)
                hmac = m.group(1)
                prefix = ''.join(hmac.split(':')[:3]).upper()

                if self._iface_name_match(iface_name):
                    vendor = oui.get_vendor(prefix)
                    vendors.add(vendor)
                else:
                    vendor = NetworkCardVendors.UNKNOWN_VENDOR

                self._root_node.system.hw.network_interfaces[iface_name] = \
                    dict(hmac=hmac, prefix=prefix, vendor=vendor, inet=[], inet6=[])
            elif 'inet' in line:
                if iface_name not in self._root_node.system.hw.network_interfaces:
                    continue

                s = line.split(' ', 1)
                inet_type = s[0].replace("\t", '')
                self._root_node.system.hw.network_interfaces[iface_name][inet_type].append(' '.join(s[1:]))

    def _process_ip_addr_output(self, content: str, vendors: set):
        oui = self._ll_node.oui
        iface_name = ''
        for line in content:
            m = re.match(r'^[0-9]+: ([^ ]+):.*', line)
            if m:
                iface_name = m.group(1)
            elif 'link/ether' in line:
                m = re.match(r'.*link/ether ([^ ]+).*', line)
                hmac = m.group(1)
                prefix = ''.join(hmac.split(':')[:3]).upper()

                if self._iface_name_match(iface_name):
                    vendor = oui.get_vendor(prefix)
                    vendors.add(vendor)
                else:
                    vendor = NetworkCardVendors.UNKNOWN_VENDOR

                self._root_node.system.hw.network_interfaces[iface_name] = \
                    dict(hmac=hmac, prefix=prefix, vendor=vendor, inet=[], inet6=[])
            elif ' inet' in line:
                if iface_name not in self._root_node.system.hw.network_interfaces:
                    continue

                s = line.split()
                self._root_node.system.hw.network_interfaces[iface_name][s[0]].append(s[1])

    def _iface_name_match(self, iface_name: str):
        for prefix in self.PREFIXES:
            # expected format: f'{prefix}{a_number}{anything}', like eth0 or eth0:1
            if iface_name.startswith(prefix) and len(iface_name) > len(prefix):
                c = iface_name[len(prefix)]
                if c == '0' or int(c) != 0:
                    return True

        return False
