#  Copyright 2022, Laszlo Attila Toth
#  Distributed under the terms of the Apache License, Version 2.0

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from .commands import CalculateCommand, PrintCommand


class ChecksumsCommand(Command):
    name = 'checksums'
    description = "Handle checksums of a files in a directory and store in SQLite"
    subcommand_classes = [
        CalculateCommand,
        PrintCommand
    ]

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option(
            '-s', '--sqlite', '-f', '--file', dest='db_filename', required=True,
            help='Database filename')


ChecksumsPlugin = CommandPlugin.create(ChecksumsCommand)
