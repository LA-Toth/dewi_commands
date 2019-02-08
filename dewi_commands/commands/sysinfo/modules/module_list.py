# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.config.config import Config
from dewi_core.logger import log_debug
from dewi_module_framework.messages import Messages
from .bash_history import BashHistoryModule
from .fs import FileSystemModule
from .graph import GraphModule
from .hw import DmiDecodeParserModule
from .network import NetworkModule

modules = [
    DmiDecodeParserModule,
    FileSystemModule,
    BashHistoryModule,
    NetworkModule,
    GraphModule,
]


def run_modules(config: Config, messages: Messages):
    for module_class in modules:
        module = module_class(config, messages)
        log_debug('Run module', dict(classs_name=module_class.__name__))
        module.run()
