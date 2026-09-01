# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_dataclass.node import Node
from dewi_utils.rrdtool.writer import GraphResult
from .system import System


class MainNode(Node):
    log_dir: str | None
    munin_dir: str | None
    processed: str

    def __init__(self):
        self.log_dir = None
        self.munin_dir = None

        self.system = System()
        self.graphs = GraphResult()

        self.processed = '1999-12-31T23:59:59+0000'
