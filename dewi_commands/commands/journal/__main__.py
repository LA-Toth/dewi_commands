# Copyright 2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_commands.commands.journal import JournalCommand
from dewi_core.application import Application


def main():
    app = Application('dewi-journal', JournalCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
