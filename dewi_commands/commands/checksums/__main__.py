#  Copyright 2022, Laszlo Attila Toth
#  Distributed under the terms of the Apache License, Version 2.0

import sys

from dewi_core.application import Application
from . import ChecksumsCommand


def main():
    app = Application('dewi-checksums', ChecksumsCommand)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
