# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.node import Node


class Filesystem(Node):
    def __init__(self):
        self.total: int = None
        self.used: int = None
        self.free: int = None
        self.usage_percent: int = None
        self.fs_type: str = None
        self.mount_path: str = None
