# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_core.miniapp import Application
from . import FetchCovidHuCommand


def main():
    app = Application('dewi-fetch-covidhu', FetchCovidHuCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
