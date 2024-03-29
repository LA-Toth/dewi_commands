# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_utils.lithurgical import print_events_of_year


class LithurgicalCommand(Command):
    name = 'lithurgical'
    aliases = []
    description = "Prints Lutheran liturgical events of a calendar year"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_argument('year', type=int, help='The calendar year')

    def run(self, ctx: ApplicationContext):
        year: int = ctx.args.year
        if year < 1600:
            print('Please specify a year not earlier than 1600')
            return 1
        if year > 2200:
            print('Please specify a year not later than 2200')
            return 1

        print_events_of_year(year)
        return


LithurgicalPlugin = CommandPlugin.create(LithurgicalCommand)
