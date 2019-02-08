# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_logparsers.loghandler import LogHandlerModule, GenericLogFileDefinition
from dewi_module_framework.messages import Messages
from .clock import ClockModule
from .ha import HaModule
from .kernel import KernelModule
from .php import PhpModule
from .postfix import PostfixModule
from .reboot import RebootModule
from .sshd import SshdModule
from ..config.sysinfoconfig import SysInfoConfig

modules = [
    ClockModule,
    HaModule,
    KernelModule,
    PhpModule,
    PostfixModule,
    RebootModule,
    SshdModule,
]


def run_parser_modules(config: SysInfoConfig, messages: Messages):
    parser = LogHandlerModule(
        config, messages,
        GenericLogFileDefinition()
    )
    for module_class in modules:
        parser.register_module(module_class)

    parser.run()
