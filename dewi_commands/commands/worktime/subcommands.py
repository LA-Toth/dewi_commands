# Copyright 2019-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path
import sys

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.config.node import Node
from dewi_core.optioncontext import OptionContext
from .worktime_main import WorktimeImporter, WorktimeManager, WorktimeProcessor


class Subcommand(Command):
    ext = 'sqlite'

    @classmethod
    def register_arguments(cls, c: OptionContext):
        c.add_option('--filename',
                     help='Filename or ~/WT.{ext} or ~/WORKTIME.{ext}'.format(ext=cls.ext))

    def _validate_filename(self, args: Node) -> bool:
        if not args.filename:
            args.filename = os.path.expanduser('~/WT.' + self.ext)
            if not os.path.exists(args.filename):
                args.filename = os.path.expanduser('~/WORKTIME.' + self.ext)

        if not os.path.exists(args.filename):
            print(f'{args.filename} does not exist. Please specify a valid file', file=sys.stderr)
            return False

        args.filename = os.path.abspath(args.filename)

        return True


class Import(Subcommand):
    name = 'import'
    aliases = ['imp']
    description = 'Import a .TXT file into the database'

    @classmethod
    def register_arguments(cls, c: OptionContext) -> None:
        Subcommand.register_arguments(c)
        c.add_option('-s', '--source', required=True, help='The source .TXT file')

    def run(self, ctx: ApplicationContext) -> int | None:
        if not self._validate_filename(ctx.args):
            return 1

        return WorktimeImporter(ctx.args.filename, ctx.args.source).run()


class Login(Subcommand):
    name = 'login'
    aliases = ['in']
    description = 'Log in'

    def run(self, ctx: ApplicationContext) -> int | None:
        if not self._validate_filename(ctx.args):
            return 1

        return WorktimeManager(ctx.args.filename).login()


class Logout(Subcommand):
    name = 'logout'
    aliases = ['out']
    description = 'Log out'

    def run(self, ctx: ApplicationContext) -> int | None:
        if not self._validate_filename(ctx.args):
            return 1

        return WorktimeManager(ctx.args.filename).logout()


class Print(Subcommand):
    name = 'print'
    aliases = ['p']
    description = 'Prints the current worktime entries and stat'
    ext = 'txt'

    @classmethod
    def register_arguments(cls, c: OptionContext) -> None:
        Subcommand.register_arguments(c)
        c.add_option('-t', '--today', is_flag=True, default=False,
                     help='Print stat of today only and the summary')

    def run(self, ctx: ApplicationContext) -> int | None:
        if not self._validate_filename(ctx.args):
            return 1

        return WorktimeProcessor(ctx.args.filename, today_only=ctx.args.today).run()
