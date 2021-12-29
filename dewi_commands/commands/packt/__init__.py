# Copyright 2018-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_commands.commands.packt.config import load_config
from dewi_commands.commands.packt.runner import run
from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class PacktCommand(Command):
    name = 'packt'
    aliases = []
    description = "Packt stuffs"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('--wait-for-close', help='Wait a minute before closing Chrome', is_flag=True)

        driver_grp = c.add_group(
            'Browser and WebDriver options',
            help='Options influences the behaviour of Selenium Web Driver and Google Chrome / Firefox')

        driver_grp.add_option('--screenshots', '--screenshot-dir', dest='screenshot_dir', default='.',
                                help='The directory to save any screenshot, default: current directory')
        driver_grp.add_option('--download-directory', '--dl-dir', dest='download_dir', required=True,
                                help='Download directory')
        driver_grp.add_option('--headless', is_flag=True, help='Start Chrome in headless mode')
        driver_grp.add_option('--timeout', type=int, default=60,
                                help='Timeout for waiting any element or action, default: 60s')

    def run(self, ctx: ApplicationContext):
        config = load_config()
        config.driver.screenshot_directory = ctx.args.screenshot_dir
        config.driver.download_directory = ctx.args.download_dir
        config.driver.headless = ctx.args.headless
        config.driver.timeout = ctx.args.timeout
        config.wait_before_close = ctx.args.wait_for_close

        return run(config)


PacktPlugin = CommandPlugin.create(PacktCommand)
