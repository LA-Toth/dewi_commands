# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_commands.commands.worktime.subcommands import Import, Login, Logout, Print, Subcommand
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class WorktimeCommand(Command):
    name = 'worktime'
    aliases = ['w', 'wt']
    description = "Calculate worktime from a file"
    subcommand_classes = [
        Import,
        Login,
        Logout,
        Print
    ]


WorktimePlugin = CommandPlugin.create(WorktimeCommand)
