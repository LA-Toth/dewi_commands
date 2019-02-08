# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.node import Node
from dewi_utils.network import NetworkCardVendors
from ..constants import Mode


class LowLevelDetails(Node):
    def __init__(self):
        self.oui: NetworkCardVendors = None
        self.dmidecode = dict()

        self.mode: Mode = Mode.NO_MODE

    def __repr__(self) -> str:
        return str(self.__dict__)
