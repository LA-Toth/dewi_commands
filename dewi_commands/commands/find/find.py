# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import typing


class Find:
    def __init__(self, directories: typing.List[str]):
        self.directories = directories

    def find(self):
        for full_path, name in self._walk():
            print(full_path)

    def _walk(self) -> typing.Iterable[typing.Tuple[str, str]]:
        for directory in self.directories:
            for root, dirs, files in os.walk(directory):
                for name in dirs:
                    full_path = os.path.join(root, name)
                    yield full_path + os.sep, name
                for name in files:
                    full_path = os.path.join(root, name)
                    yield full_path, name
