# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from .processors import Processor


class SysInfoCommand(Command):
    name = 'sysinfo'
    aliases = ['debug-info']
    description = "Examine the system and creates a summary in HTML & YAML form"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--reprocess', '-f', '--force', action='store_true', dest='reprocess', default=False,
                            help='Reprocess sysinfo if generated YAML file exists')
        parser.add_argument('--output', '-o', dest='output_dir', required=True,
                            help='Output directory for result.yaml and index.html')
        parser.add_argument('--munin-dir', '-m', dest='munin_dir', default='/var/lib/munin',
                            help='Munin directory, may not exist, default: /var/lib/munin')
        parser.add_argument('--log-dir', '-l', dest='log_dir', default='/var/log',
                            help='Log directory, may not exist, default: /var/log')

        parser.add_argument('--no-logs', '-L', action='store_true', dest='no_log', default=False,
                            help='Skip processing logs')
        parser.add_argument('--no-graphs', '-G', action='store_true', dest='no_graph', default=False,
                            help='Skip generating munin graphs')

    def run(self, args: argparse.Namespace):
        p = Processor(args.log_dir, args.munin_dir, args.output_dir, args.reprocess, not args.no_log, not args.no_graph)
        return p.process()


SysInfoPlugin = CommandPlugin.create(SysInfoCommand)
