# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from .fetch import Fetcher


class FetchCovidHuCommand(Command):
    name = 'fetch-covid-hu'
    aliases = ['fetch-koronavirus.gov.hu']
    description = 'Fetches the koronavirus.gov.hu site into CSV/JPG'

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-a', '--historical', '--archived', is_flag=True,
                     dest='historical', help='Fetch all historical data (missing from directory)')
        c.add_argument(
            'directory', nargs=1,
            help='The output base directory - a subdirectory from localtime will be created')

    def run(self, ctx: ApplicationContext):
        return Fetcher(ctx.args.directory, historical_mode=ctx.args.historical).fetch()


FetchCovidHuPlugin = CommandPlugin.create(FetchCovidHuCommand)
