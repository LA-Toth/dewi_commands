# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import re
import subprocess

from ..common.base_module_ import BaseModule


class DmiDecodeParserModule(BaseModule):
    def provide(self):
        return 'dmidecode'

    def run(self):
        self._parse_dmidecode()
        self._fill_hw_details()

    def _parse_dmidecode(self):
        first = False
        config_entry, entry = self._init_entries()

        content = subprocess.check_output('dmidecode').decode('UTF-8')

        for line in content.splitlines():
            line = line.split('\n')[0]
            if not line:
                first = True
                config_entry, entry = self._init_entries()
                continue

            if not first:
                continue

            if not line.startswith('\t'):
                if line.startswith('Handle '):
                    continue

                if line.startswith('End Of Table'):
                    break

                config_entry, entry = self._init_entries(line)
                continue

            tabs = line.count('\t')

            if ':' in line:
                key, value = line.strip().split(':', 1)

                if tabs <= len(entry):
                    entry = entry[0:tabs]
                entry.append(key)

                config_entry = '_ll.dmidecode.{}'.format('.'.join(entry))

                value = value.strip()
                if value:
                    self.set(config_entry, value)
            else:
                line = line.strip()

                orig = self.get(config_entry)
                if isinstance(orig, str) and re.match(r'^ *[0-9]+$', orig):
                    self.set(config_entry, dict(count=orig, values=[]))
                    config_entry += '.values'

                self.append(config_entry, line)

    def _init_entries(self, last_item: str | None = None):
        entry = [last_item] if last_item else []
        config_entry = '_ll.dmidecode.{}'.format('.'.join(entry))
        return config_entry, entry

    def _fill_hw_details(self):
        self.set('root.system.hw.dmidecode.manufacturer',
                 self.get('_ll.dmidecode.System Information.Manufacturer'))
        self.set('root.system.hw.dmidecode.product',
                 self.get('_ll.dmidecode.System Information.Product Name'))
        self.set('root.system.hw.dmidecode.serial',
                 self.get('_ll.dmidecode.System Information.Serial Number'))
        self.set('root.system.hw.dmidecode.uuid',
                 self.get('_ll.dmidecode.System Information.UUID'))
