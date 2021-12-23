# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from .find import Find


class FindCommand(Command):
    name = 'find'
    description = 'Partial implementation of UNIX "find" tool'

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_argument(
            'directories', nargs=-1,
            help='The search directories')

    def run(self, ctx: ApplicationContext):
        return Find(ctx.args.directories or ['.']).find()


FindPlugin = CommandPlugin.create(FindCommand)
