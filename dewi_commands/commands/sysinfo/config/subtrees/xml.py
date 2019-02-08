# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from xml.etree import ElementTree

from dewi_core.config.node import Node


class Xml(Node):
    def __init__(self):
        self.root: ElementTree = None
