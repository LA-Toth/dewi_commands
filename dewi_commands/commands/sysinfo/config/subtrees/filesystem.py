# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_dataclass.node import Node


class Filesystem(Node):
    total: int | None
    used: int | None
    free: int | None
    usage_percent: int | None
    fs_type: str | None
    mount_path: str | None

    def __init__(self):
        self.total = None
        self.used = None
        self.free = None
        self.usage_percent = None
        self.fs_type = None
        self.mount_path = None
