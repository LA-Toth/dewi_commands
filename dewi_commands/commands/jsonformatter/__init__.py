# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import json

from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin


class JsonFormatterCommand(Command):
    name = 'jsonformatter'
    aliases = ['json-formatter', 'format-json', 'formatj', 'jsonf']
    description = "Read a JSON file and write it with indentation and in UTF-8 encoding"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('source', nargs=1, help='The source file')
        parser.add_argument('destination', nargs=1, help='The destination file')

    def run(self, args: argparse.Namespace):
        with open(args.source[0]) as f:
            input_json = json.load(f)

        with open(args.destination[0], 'wt', encoding='UTF-8') as f:
            json.dump(input_json, f, indent=2, ensure_ascii=False)
            f.write("\n")


JSonFormatterPlugin = CommandPlugin.create(JsonFormatterCommand)
