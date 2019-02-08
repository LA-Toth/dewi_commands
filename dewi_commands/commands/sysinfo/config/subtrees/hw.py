# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.node import Node


class DmiDecode(Node):
    def __init__(self):
        self.manufacturer: str = None
        self.product: str = None
        self.serial: str = None
        self.uuid: str = None


class RAID(Node):
    def __init__(self):
        self.controller: str = None
        self.subsystem: str = None
        self.driver: str = None


class Hardware(Node):
    def __init__(self):
        self.mem_size: int = None
        self.mem_free: int = None
        self.mem_mapped: int = None
        self.network_interfaces = dict()
        self.dmidecode = DmiDecode()
        self.raid = RAID()
        self.pci: str = None
        self.has_xvd: bool = None
        self.disk_capacity: int = None
