# Copyright 2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_commands.commands.stocks import StocksCommand
from dewi_core.application import Application


def main():
    app = Application('dewi-stocks', StocksCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
