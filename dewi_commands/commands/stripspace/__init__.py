# Copyright 2010-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import subprocess

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_core.utils.time import localtime


class StripSpaceCommand(Command):
    name = 'stripspace'
    aliases = ['str']
    description = 'Removes extra whitespace characters'

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-i', '--in-place', dest='inplace', is_flag=True, help='Strip spaces in-place')
        c.add_option('-b', '--backup-suffix', dest='backup_suffix',
                     help="Create backup files with suffix (for in-place case), e.g. '.bak'", metavar='SUFFIX')

        c.add_argument('file_list', nargs=-1, required=True, help='List of filenames for striping spaces')

    def run(self, ctx: ApplicationContext):
        ltime = localtime()
        for filename in ctx.current_args.file_list:
            if os.path.exists(filename):
                try:
                    if ctx.current_args.inplace:
                        if ctx.current_args.backup_suffix:
                            subprocess.run(['cp', '-a', filename, filename + ctx.current_args.backup_suffix],
                                           check=True)

                        # We would like to preserve the permissions, so we do not want to move the temporary file
                        temp_filename = f"{filename}.{ltime}"
                        subprocess.run(
                            "git stripspace > '%(temp_filename)s' < '%(filename)s' && cat '%(temp_filename)s' > '%(filename)s' && rm '%(temp_filename)s'" % {
                                'temp_filename': temp_filename, 'filename': filename},
                            check=True, shell=True
                        )
                    else:
                        subprocess.run("git stripspace > '%s.%s' < '%s'" % (filename, ltime, filename),
                                       check=True, shell=True)
                except subprocess.CalledProcessError as e:
                    print("dewi %s failed for file '%s'; error_code='%d'" % (self.name, filename, e.returncode))
            else:
                print("Error: '%s' not found" % (filename,))


StripSpacePlugin = CommandPlugin.create(StripSpaceCommand)
