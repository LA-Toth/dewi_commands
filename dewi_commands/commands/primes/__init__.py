# Copyright 2018-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class PrimeGenerator:
    def __init__(self, smaller_than: int | None, count: int | None):
        self.smaller_than = smaller_than
        self.count = count

    def run(self):
        # from https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
        print(2)

        count = 1
        possible_prime = 3
        while True:
            if self.smaller_than is not None and possible_prime > self.smaller_than:
                break

            # Assume number is prime until shown it is not.
            is_prime = True
            for num in range(2, int(possible_prime ** 0.5) + 1):
                if possible_prime % num == 0:
                    is_prime = False
                    break

            if is_prime:
                print(possible_prime)
                count += 1

            if self.count is not None and count >= self.count:
                break

            possible_prime += 1


class PrimesCommand(Command):
    name = 'primes'
    aliases = ['prime']
    description = "Calculate first N primes"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-s', '--smaller-than', dest='smaller_than', type=int,
                     help='Print till the primes are smaller than this value.')
        c.add_option('-c', '--count', type=int,
                     help='Max number of printed primes (if --smaller-than is not specified, count is 100)')

    def run(self, ctx: ApplicationContext):
        if ctx.args.smaller_than is None and ctx.args.count is None:
            ctx.args.count = 100

        p = PrimeGenerator(ctx.args.smaller_than, ctx.args.count)
        return p.run()


PrimesPlugin = CommandPlugin.create(PrimesCommand)
