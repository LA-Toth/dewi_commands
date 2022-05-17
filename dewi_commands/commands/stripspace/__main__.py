# Copyright 2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_commands.commands.stripspace import StripSpaceCommand
from dewi_core.application import Application


def main():
    app = Application('dewi-stripspace', StripSpaceCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
