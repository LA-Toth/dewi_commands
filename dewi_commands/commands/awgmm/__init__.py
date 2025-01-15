# Copyright 2025 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import math

import click

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class AwgMmCommand(Command):
    name = 'awgmm'
    description = 'Converts between AWG, mm, and mm^2'

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('--from', type=click.Choice(['awg', 'mm', 'mm2']), default='awg', dest='convert_from',
                     help='Convert from specified setting')

        c.add_argument('value', type=float,
                       help='Value to be converted')

    def run(self, ctx: ApplicationContext):
        value = ctx.current_args.value
        if ctx.current_args.convert_from == 'awg':
            d = self._awg_to_mm(value)
            print(f'Converting from AWG {value}')
            print(f'   = {round(value)} AWG')
            print(f'   = {d:.4f} mm')
            print(f'   = {math.pi / 4 * d * d :.4f} mm2')

        elif ctx.current_args.convert_from == 'mm':
            awg = self._mm_to_awg(value)
            print(f'Converting from {value} mm')
            print(f'   = {awg} AWG')
            print(f'   = {value} mm')
            print(f'   = {math.pi / 4 * value * value:.4f} mm2')

        else:  # ctx.current_args.convert_from == 'mm2':
            mm = math.sqrt(4 * value / math.pi)
            print(f'Converting from {value} mm2')
            print(f'   = {self._mm_to_awg(mm)} AWG')
            print(f'   = {mm:.4f} mm')
            print(f'   = {value:.4f} mm2')

    def _awg_to_mm(self, awg):
        return 0.127 * (92 ** ((36 - awg) / 39))

    def _mm_to_awg(self, mm):
        return round(36 - 39 * math.log(mm / 0.127, 92))


AwgMmPlugin = CommandPlugin.create(AwgMmCommand)
