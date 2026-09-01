# Copyright 2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import tempfile
from types import SimpleNamespace

import dewi_core.testcase

from dewi_commands.commands.journal.journal_commands import NewCommand, SubCommand


class _FakeOptionContext:
    def __init__(self):
        self.options = []

    def add_option(self, *args, **kwargs):
        self.options.append((args, kwargs))


class SubCommandTest(dewi_core.testcase.TestCase):
    def set_up(self):
        self._original_config_file_name = SubCommand.CONFIG_FILE_NAME
        self._tmpdir = tempfile.TemporaryDirectory()
        self._tmpfile = os.path.join(self._tmpdir.name, 'dewi_journal.ini')
        SubCommand.CONFIG_FILE_NAME = self._tmpfile

    def tear_down(self):
        SubCommand.CONFIG_FILE_NAME = self._original_config_file_name
        self._tmpdir.cleanup()

    def _write_config(self, content: str):
        with open(self._tmpfile, 'wt', encoding='UTF-8') as f:
            f.write(content)

    def test_register_arguments_requires_options_without_config(self):
        c = _FakeOptionContext()
        SubCommand.register_arguments(c)

        self.assert_equal(2, len(c.options))
        self.assert_true(c.options[0][1]['required'])
        self.assert_true(c.options[1][1]['required'])

    def test_register_arguments_makes_options_optional_with_config(self):
        self._write_config(
            '[journal]\n'
            'directory=/tmp/journal\n'
            'daily-note-template-file=/tmp/template.txt\n'
        )
        c = _FakeOptionContext()
        SubCommand.register_arguments(c)

        self.assert_false(c.options[0][1]['required'])
        self.assert_false(c.options[1][1]['required'])

    def test_run_uses_config_values_as_defaults(self):
        self._write_config(
            '[journal]\n'
            'directory=/tmp/journal\n'
            'daily-note-template-file=/tmp/template.txt\n'
        )
        cmd = NewCommand()
        ctx = SimpleNamespace(args=SimpleNamespace(journal_dir=None, template_file=None))

        cmd.run(ctx)

        self.assert_equal('/tmp/journal', cmd.journal_dir)
        self.assert_equal('/tmp/template.txt', cmd.daily_note_template_file)

    def test_run_overrides_config_values_with_options(self):
        self._write_config(
            '[journal]\n'
            'directory=/tmp/journal\n'
            'daily-note-template-file=/tmp/template.txt\n'
        )
        cmd = NewCommand()
        ctx = SimpleNamespace(args=SimpleNamespace(
            journal_dir='/override/journal',
            template_file='/override/template.txt'
        ))

        cmd.run(ctx)

        self.assert_equal('/override/journal', cmd.journal_dir)
        self.assert_equal('/override/template.txt', cmd.daily_note_template_file)
