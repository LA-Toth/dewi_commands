# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_core.application import MainApplication
from dewi_core.loader.loader import PluginLoader


def main():
    loader = PluginLoader()
    app = MainApplication(loader, 'dewi-sysinfo',
                          fallback_to_plugin_name='dewi_commands.commands.sysinfo.SysInfoPlugin',
                          disable_plugins_from_cmdline=True)
    app.run(sys.argv[1:])


if __name__ == '__main__':
    main()
