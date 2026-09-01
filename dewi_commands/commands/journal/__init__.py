# Copyright 2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from .journal_commands import NewCommand, NewInRangeCommand


class JournalCommand(Command):
    name = 'journal'
    aliases = ['j']
    description = "Daily Journal related commands"

    subcommand_classes = [
        NewInRangeCommand,
        NewCommand
    ]


JournalPlugin = CommandPlugin.create(JournalCommand)
