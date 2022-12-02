#  Copyright 2021-2022, Laszlo Attila Toth
#  Distributed under the terms of the GNU Lesser General Public License v3

import subprocess
import typing

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class BashCommand(Command):
    name = 'shell'
    aliases = ['bash', 'sh']
    description = 'Run bash'

    def run(self, ctx: ApplicationContext) -> typing.Optional[int]:
        return subprocess.run(['/usr/bin/env', 'bash']).returncode


BashPlugin = CommandPlugin.create(BashCommand)
