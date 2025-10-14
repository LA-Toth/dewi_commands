# Copyright 2025, Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_core.application import Application
from . import RunTestsCommand


def main():
    app = Application('dewi-run-tests', RunTestsCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
