# Copyright 2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_utils.files import python_repo_hash_md5


class HashCommand(Command):
    name = 'hash'
    description = 'Runs hash-related tasks'

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose',
                            help='Verbose output, prints the details of hashed values')

        grp = parser.add_mutually_exclusive_group(required=True)
        grp.add_argument('--phash', '--python-hash', dest='phash', metavar='PYTHON-DIR',
                         help='Calculate MD5 hex digest of a directory without .git and __pychache__')

    def run(self, args: argparse.Namespace):
        if args.phash:
            print(python_repo_hash_md5(args.phash, verbose=args.verbose))


HashPlugin = CommandPlugin.create(HashCommand)
