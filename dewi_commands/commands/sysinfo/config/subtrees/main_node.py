# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.node import Node
from dewi_utils.rrdtool.writer import GraphResult
from .system import System


class MainNode(Node):
    def __init__(self):
        self.log_dir: str = None
        self.munin_dir: str = None

        self.system = System()
        self.graphs = GraphResult()

        self.processed: str = '1999-12-31T23:59:59+0000'
