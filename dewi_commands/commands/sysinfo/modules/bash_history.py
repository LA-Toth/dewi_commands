# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import os.path
import re

from dewi_core.config.node import Node
from dewi_module_framework.messages import Level
from ..common.base_module_ import BaseModule


class BashEntry(Node):
    def __init__(self):
        self.timestamp: datetime.datetime = None
        self.lines: list[str] = []


class BashHistoryModule(BaseModule):
    def provide(self):
        return 'bash_history'

    def run(self):
        filename = os.path.expanduser('~/.bash_history')

        if not os.path.exists(filename):
            return

        entries: list[BashEntry] = []
        entry: BashEntry = None

        with open(filename) as f:
            for line in f:
                line = line.rstrip('\n')

                if line.startswith('#') and re.match(r'^#1[0-9]+$', line):
                    entry = BashEntry()
                    entry.timestamp = datetime.datetime.fromtimestamp(int(line[1:]))
                    entries.append(entry)
                else:
                    if entry:
                        entry.lines.append(line)
                    else:
                        entry = BashEntry()
                        entry.timestamp = datetime.datetime.fromtimestamp(42)
                        entry.lines.append(line)
                        entries.append(entry)

        history_lines = []

        for entry in entries:
            for line in entry.lines:
                history_lines.append(f'{entry.timestamp} - {line}')

        self.add_message(
            Level.INFO,
            'User',
            f'Bash History',
            f'Bash History', details=history_lines
        )
