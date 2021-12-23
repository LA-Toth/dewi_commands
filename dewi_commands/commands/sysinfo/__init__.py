# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from .processors import Processor


class SysInfoCommand(Command):
    name = 'sysinfo'
    aliases = ['debug-info']
    description = "Examine the system and creates a summary in HTML & YAML form"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('--reprocess', '-f', '--force', is_flag=True, dest='reprocess', default=False,
                     help='Reprocess sysinfo if generated YAML file exists')
        c.add_option('--output', '-o', dest='output_dir', required=True,
                     help='Output directory for result.yaml and index.html')
        c.add_option('--munin-dir', '-m', dest='munin_dir', default='/var/lib/munin',
                     help='Munin directory, may not exist, default: /var/lib/munin')
        c.add_option('--log-dir', '-l', dest='log_dir', default='/var/log',
                     help='Log directory, may not exist, default: /var/log')

        c.add_option('--no-logs', '-L', is_flag=True, dest='no_log', default=False,
                     help='Skip processing logs')
        c.add_option('--no-graphs', '-G', is_flag=True, dest='no_graph', default=False,
                     help='Skip generating munin graphs')

    def run(self, ctx: ApplicationContext):
        p = Processor(ctx.args.log_dir, ctx.args.munin_dir, ctx.args.output_dir, ctx.args.reprocess,
                      not ctx.args.no_log, not ctx.args.no_graph)
        return p.process()


SysInfoPlugin = CommandPlugin.create(SysInfoCommand)
