# Copyright 2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import os
from datetime import date, timedelta

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.config.iniconfig import IniConfig
from dewi_core.optioncontext import OptionContext


class SubCommand(Command):
    CONFIG_FILE_NAME = '/path/to/dewi_journal.ini'

    def __init__(self) -> None:
        self.journal_dir: str = None
        self.daily_note_template_file: str = None

    @staticmethod
    def _read_journal_config_values() -> tuple[str | None, str | None]:
        if not os.path.exists(SubCommand.CONFIG_FILE_NAME):
            return None, None

        cfg = IniConfig()
        cfg.open(SubCommand.CONFIG_FILE_NAME)

        return (
            cfg.get('journal', 'directory'),
            cfg.get('journal', 'daily-note-template-file')
        )

    @staticmethod
    def register_arguments(c: OptionContext):
        journal_dir, daily_note_template_file = SubCommand._read_journal_config_values()

        c.add_option(
            '--journal-dir',
            type=str,
            required=journal_dir is None,
            help='Directory where journal files are stored')
        c.add_option(
            '--template-file',
            type=str,
            required=daily_note_template_file is None,
            help='Path to the template file for new journal entries')



    def run(self, ctx: ApplicationContext) -> int | None:
        journal_dir, daily_note_template_file = self._read_journal_config_values()

        self.journal_dir = journal_dir
        self.daily_note_template_file = daily_note_template_file

        journal_dir_opt = getattr(ctx.args, 'journal_dir', None)
        template_file_opt = getattr(ctx.args, 'template_file', None)

        if journal_dir_opt is not None:
            self.journal_dir = journal_dir_opt

        if template_file_opt is not None:
            self.daily_note_template_file = template_file_opt

        return self._run(ctx)


    def _run(self, ctx: ApplicationContext) -> int | None:
        pass

    def _create_template(self, for_date: str):
        output_file = f"{self.journal_dir}/{for_date}.md"

        if os.path.exists(output_file):
            return

        with open(self.daily_note_template_file, 'rt', encoding='UTF-8') as f:
            template = f.read()

        content = template.replace('{{date}}', for_date)

        with open(output_file, 'wt', encoding='UTF-8') as f:
            f.write(content)


class NewCommand(SubCommand):
    name = 'new'
    help = 'Create a new journal file'
    description = 'Create a new journal file'

    def _run(self, ctx: ApplicationContext) -> int | None:
        today = date.today().isoformat()
        self._create_template(today)




class NewInRangeCommand(SubCommand):
    name = 'new_in_range'
    help = 'Create new journal files in a specified date range'
    description = 'Create new journal files in a specified date range'

    @staticmethod
    def register_arguments(c: OptionContext):
        SubCommand.register_arguments(c)
        c.add_argument('start-date', type=str, required=True, help='Start date in YYYY-MM-DD format')
        c.add_argument('end-date', type=str, required=True, help='End date in YYYY-MM-DD format')

    def _run(self, ctx: ApplicationContext) -> int | None:
        current_day = date.fromisoformat(ctx.args.start_date)
        last_day = date.fromisoformat(ctx.args.end_date)

        while current_day <= last_day:
            if current_day.weekday() < 5:
                self._create_template(current_day.isoformat())
            current_day += timedelta(days=1)
