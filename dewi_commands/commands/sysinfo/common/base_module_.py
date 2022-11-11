# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path
from abc import ABCMeta
from xml.etree.ElementTree import Element

from dewi_core.config.config import Config
from dewi_logparsers.loghandler import LogParserModule
from dewi_module_framework.messages import Messages
from dewi_module_framework.module import Module
from ..config.sysinfoconfig import SysInfoConfig


class BaseModule(Module, metaclass=ABCMeta):
    def __init__(self, config: Config, messages: Messages):
        if not isinstance(config, SysInfoConfig):
            raise ValueError("Config's type must be SysInfoConfig")

        super().__init__(config, messages, add_messages_to_config=True)

        self._dp_config: SysInfoConfig = config
        self._root_node = self._dp_config.get_main_node()
        self._ll_node = self._dp_config.get_low_level_details()

    def _read(self, filename: str) -> tuple[bool, str | None]:
        """
        Reads a file's content and returns (exists, content) tuple
        The return value is either (False, None) or (True, content).

        :param filename: the file path
        :return: (exists, content) tuple
        """
        if not os.path.exists(filename):
            return False, None
        else:
            with open(filename) as f:
                return True, f.read()


class XmlBasedModule(BaseModule, metaclass=ABCMeta):
    def _get_element_by_id(self, id: str) -> Element | None:
        return self.get('xml.root').find(".//*[@id='{}']".format(id))


class LogparserBaseModule(LogParserModule):
    def __init__(self, config: Config, messages: Messages):
        if not isinstance(config, SysInfoConfig):
            raise ValueError("Config's type must be SysInfoConfig")

        super().__init__(config, messages, add_messages_to_config=True)
        self._dp_config: SysInfoConfig = config
        self._root_node = self._dp_config.get_main_node()
        self._ll_node = self._dp_config.get_low_level_details()
