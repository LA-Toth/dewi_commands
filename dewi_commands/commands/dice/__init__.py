# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_commands.commands.dice.die import Die
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class DiceCommand(Command):
    name = 'dice'
    aliases = ['d20']
    description = "Roll one or more dice"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            'dice', default='d6', nargs='*',
            help='The dice (or die) to roll, based on DnD: [count]d{4,6,8,10,12,20,%%}, default=d6')

    def run(self, args: argparse.Namespace):
        dice = Die()
        for d in args.dice:
            dice.roll(d)


DicePlugin = CommandPlugin.create(DiceCommand)
