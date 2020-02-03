# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_commands.commands.sort_photos import PhotoSorterCommand
from dewi_core.application import SingleCommandApplication


def main():
    app = SingleCommandApplication('dewi-sort-photos', PhotoSorterCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
