# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_dataclass.node import Node


class DmiDecode(Node):
    manufacturer: str | None
    product: str | None
    serial: str | None
    uuid: str | None

    def __init__(self):
        self.manufacturer = None
        self.product = None
        self.serial = None
        self.uuid = None


class RAID(Node):
    controller: str | None
    subsystem: str | None
    driver: str | None

    def __init__(self):
        self.controller = None
        self.subsystem = None
        self.driver = None


class Hardware(Node):
    mem_size: int | None
    mem_free: int | None
    mem_mapped: int | None
    pci: str | None
    has_xvd: bool | None
    disk_capacity: int | None

    def __init__(self):
        self.mem_size = None
        self.mem_free = None
        self.mem_mapped = None
        self.network_interfaces = dict()
        self.dmidecode = DmiDecode()
        self.raid = RAID()
        self.pci = None
        self.has_xvd = None
        self.disk_capacity = None
