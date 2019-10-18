# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import os.path
import sys
import typing

from dewi_core.command import Command
from .worktime_main import WorktimeImporter, WorktimeManager, WorktimeProcessor


class Subcommand(Command):
    ext = 'sqlite'

    def _validate_filename(self, args: argparse.Namespace) -> bool:
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

    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-s', '--source', required=True, help='The source .TXT file')

    def run(self, args: argparse.Namespace) -> typing.Optional[int]:
        if not self._validate_filename(args):
            return 1

        return WorktimeImporter(args.filename, args.source).run()


class Login(Subcommand):
    name = 'login'
    aliases = ['in']
    description = 'Log in'

    def run(self, args: argparse.Namespace) -> typing.Optional[int]:
        if not self._validate_filename(args):
            return 1

        return WorktimeManager(args.filename).login()


class Logout(Subcommand):
    name = 'logout'
    aliases = ['out']
    description = 'Log out'

    def run(self, args: argparse.Namespace) -> typing.Optional[int]:
        if not self._validate_filename(args):
            return 1

        return WorktimeManager(args.filename).logout()


class Print(Subcommand):
    name = 'print'
    aliases = ['p']
    description = 'Prints the current worktime entries and stat'
    ext = 'txt'

    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-t', '--today', action='store_true', default=False,
                            help='Print stat of today only and the summary')

    def run(self, args: argparse.Namespace) -> typing.Optional[int]:
        if not self._validate_filename(args):
            return 1

        return WorktimeProcessor(args.filename, today_only=args.today).run()
