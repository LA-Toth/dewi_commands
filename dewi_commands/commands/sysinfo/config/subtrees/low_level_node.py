# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_dataclass.node import Node
from dewi_utils.network import NetworkCardVendors
from ..constants import Mode


class LowLevelDetails(Node):
    oui: NetworkCardVendors | None
    mode: Mode

    def __init__(self):
        self.oui = None
        self.dmidecode = dict()

        self.mode = Mode.NO_MODE

    def __repr__(self) -> str:
        return str(self.__dict__)
