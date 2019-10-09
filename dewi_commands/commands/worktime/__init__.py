# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import typing

from dewi_commands.commands.worktime.subcommands import Subcommand, Import, Login, Logout, Print
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class WorktimeCommand(Command):
    name = 'worktime'
    aliases = ['w', 'wt']
    description = "Calculate worktime from a file"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parsers = parser.add_subparsers(title='Subcommand for specific locations', dest='cmd', required=True)
        self._add_parser(parsers, Import)
        self._add_parser(parsers, Login)
        self._add_parser(parsers, Logout)
        self._add_parser(parsers, Print)

    def _add_parser(self, parsers, subcommand: typing.Type[Subcommand]):
        cmd = subcommand()
        _parser = parsers.add_parser(cmd.name, help=cmd.description, aliases=cmd.aliases)
        cmd.register_arguments(_parser)
        _parser.set_defaults(func=cmd.run, instance=cmd)
        _parser.add_argument('filename', nargs='?',
                             help='Filename or ~/WT.{ext} or ~/WORKTIME.{ext}'.format(ext=subcommand.ext))

    def run(self, args: argparse.Namespace):
        return args.func(args)


WorktimePlugin = CommandPlugin.create(WorktimeCommand)
