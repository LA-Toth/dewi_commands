# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from .fetch import Fetcher


class FetchCovidHuCommand(Command):
    name = 'fetch-covid-hu'
    aliases = ['fetch-koronavirus.gov.hu']
    description = 'Fetches the koronavirus.gov.hu site into CSV/JPG'

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('-a', '--historical', '--archived', action='store_true',
                            dest='historical', help='Fetch all historical data (missing from directory)')
        parser.add_argument(
            'directory', nargs=1,
            help='The output base directory - a subdirectory from localtime will be created')

    def run(self, args: argparse.Namespace):
        return Fetcher(args.directory[0], historical_mode=args.historical).fetch()


FetchCovidHuPlugin = CommandPlugin.create(FetchCovidHuCommand)
