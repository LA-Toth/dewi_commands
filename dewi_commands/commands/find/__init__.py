# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from .find import Find


class FindCommand(Command):
    name = 'find'
    description = 'Partial implementation of UNIX "find" tool'

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            'directory', default='.', nargs='*',
            help='The search directory')

    def run(self, args: argparse.Namespace):
        return Find(args.directory).find()


FindPlugin = CommandPlugin.create(FindCommand)
