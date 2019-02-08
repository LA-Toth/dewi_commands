# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.config import Config as FwConfig
from .subtrees.low_level_node import LowLevelDetails
from .subtrees.main_node import MainNode
from .subtrees.xml import Xml


class SysInfoConfig(FwConfig):
    def __init__(self):
        super().__init__()
        self.set('_ll', LowLevelDetails())
        self.set('root', MainNode())
        self.set('xml', Xml())

    def get_low_level_details(self) -> LowLevelDetails:
        return self.get('_ll')

    def get_main_node(self) -> MainNode:
        return self.get('root')

    def get_xml_node(self) -> Xml:
        return self.get('xml')

    def overwrite_config(self, config: dict):
        self.get_main_node().load_from(config['root'])
        for key in config:
            if key != 'root':
                self._top_level_unsafe_set(key, config[key])
