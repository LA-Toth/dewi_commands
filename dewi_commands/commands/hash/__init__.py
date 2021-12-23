# Copyright 2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_utils.files import python_repo_hash_md5


class HashCommand(Command):
    name = 'hash'
    description = 'Runs hash-related tasks'

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-v', '--verbose', is_flag=True, default=False, dest='verbose',
                     help='Verbose output, prints the details of hashed values')

        grp = c.add_mutually_exclusive_group(required=True)
        grp.add_option('--phash', '--python-hash', dest='phash', metavar='PYTHON-DIR',
                       help='Calculate MD5 hex digest of a directory without .git and __pychache__')

    def run(self, ctx: ApplicationContext):
        if ctx.args.phash:
            print(python_repo_hash_md5(ctx.args.phash, verbose=ctx.args.verbose))


HashPlugin = CommandPlugin.create(HashCommand)
