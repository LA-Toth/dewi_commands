# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_commands.commands.dice.die import Die
from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class DiceCommand(Command):
    name = 'dice'
    aliases = ['d20']
    description = "Roll one or more dice"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_argument(
            'dice', nargs=-1,
            help='The dice (or die) to roll, based on DnD: [count]d{4,6,8,10,12,20,%%}, default=d6')

    def run(self, ctx: ApplicationContext):
        dice = Die()
        for d in ctx.args.dice or ['d6']:
            dice.roll(d)


DicePlugin = CommandPlugin.create(DiceCommand)
