# Copyright 2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_commands.commands.stocks.stocks import StocksProcessor
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class StocksCommand(Command):
    name = 'stocks'
    description = "Calculate gain/loss and others based on " \
                  "DATE;ACTION;SOCK;PRICE;SHARE-PRICE;SHARE-AMOUNT"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('-i', '--input', required=True,
                            help='The CSV file to process')
        parser.add_argument('-o', '--output', required=False,
                            help='The output CSV filename')

    def run(self, args: argparse.Namespace):
        StocksProcessor(args.input, args.output).process()


StocksPlugin = CommandPlugin.create(StocksCommand)
