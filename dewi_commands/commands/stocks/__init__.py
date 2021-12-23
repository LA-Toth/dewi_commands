# Copyright 2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_commands.commands.stocks.stocks import StocksProcessor
from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class StocksCommand(Command):
    name = 'stocks'
    description = "Calculate gain/loss and others based on " \
                  "DATE;ACTION;SOCK;PRICE;SHARE-PRICE;SHARE-AMOUNT"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-i', '--input', required=True,
                     help='The CSV file to process')
        c.add_option('-o', '--output', required=False,
                     help='The output CSV filename')

    def run(self, ctx: ApplicationContext):
        StocksProcessor(ctx.args.input, ctx.args.output).process()


StocksPlugin = CommandPlugin.create(StocksCommand)
