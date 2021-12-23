# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import json

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class JsonFormatterCommand(Command):
    name = 'jsonformatter'
    aliases = ['json-formatter', 'format-json', 'formatj', 'jsonf']
    description = "Read a JSON file and write it with indentation and in UTF-8 encoding"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_argument('source', nargs=1, help='The source file')
        c.add_argument('destination', nargs=1, help='The destination file')

    def run(self, ctx: ApplicationContext):
        with open(ctx.args.source) as f:
            input_json = json.load(f)

        with open(ctx.args.destination, 'wt', encoding='UTF-8') as f:
            json.dump(input_json, f, indent=2, ensure_ascii=False)
            f.write("\n")


JSonFormatterPlugin = CommandPlugin.create(JsonFormatterCommand)
