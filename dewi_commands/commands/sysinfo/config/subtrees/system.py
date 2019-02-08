# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.node import Node, NodeList
from .filesystem import Filesystem
from .hw import Hardware


class System(Node):
    def __init__(self):
        self.hw = Hardware()
        self.filesystems = NodeList(Filesystem)
        self.hostname: str = None
