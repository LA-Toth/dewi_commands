# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import subprocess

from dewi_module_framework.messages import Level
from ..common.base_module_ import BaseModule
from ..config.subtrees.filesystem import Filesystem


class FileSystemModule(BaseModule):
    ALERT_IF_USAGE_ABOVE = 90
    WARNING_IF_USAGE_ABOVE = 80

    SUFFIX_MAP = {
        'K': 1,
        'M': 1024 ** 1,
        'G': 1024 ** 2,
        'T': 1024 ** 3,
        'P': 1024 ** 4,
    }

    def provide(self):
        return 'fs'

    def run(self):
        output = subprocess.check_output(['gdf', '-h']).decode('UTF-8')
        idx = 0
        for line in output.splitlines():
            idx += 1
            if idx == 1:
                continue

            line = line.split('\n')[0]
            parts = [x for x in line.split(' ') if x]
            fs = parts[0]
            target = parts[5]  # 8 if macOS + builtin df

            total = float(parts[1][:-1].replace(',', '.')) * self.SUFFIX_MAP[parts[1][-1]]
            used = float(parts[2][:-1].replace(',', '.')) * self.SUFFIX_MAP[parts[2][-1]]
            free = float(parts[3][:-1].replace(',', '.')) * self.SUFFIX_MAP[parts[3][-1]]
            usage = int(parts[4][:-1].replace(',', '.'))  # drop % char

            entry = Filesystem()

            entry.total = int(total)
            entry.used = int(used)
            entry.free = int(free)
            entry.usage_percent = usage
            entry.mount_path = target

            self._root_node.system.filesystems.append(entry)

            if usage > self.ALERT_IF_USAGE_ABOVE:
                level = Level.ALERT
            elif usage > self.WARNING_IF_USAGE_ABOVE:
                level = Level.WARNING
            else:
                level = Level.INFO

            self.add_message(
                level,
                'Filesystem', 'Disk usage',
                f'{entry.mount_path} uses {usage}% of available space'
            )
