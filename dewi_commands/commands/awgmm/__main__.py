# Copyright 2025 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_commands.commands.awgmm import AwgMmCommand
from dewi_core.application import Application


def main():
    app = Application('dewi-awgmm', AwgMmCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
