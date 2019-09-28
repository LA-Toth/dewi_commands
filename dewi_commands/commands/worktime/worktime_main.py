# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import re
import time
import typing

from dewi_commands.commands.worktime.database import create_database_manager
from dewi_commands.commands.worktime.models.worktime_entry import WorktimeEntry
from dewi_core.logger import log_debug


class Entry:
    def __init__(self, date: str, intervals: typing.List[typing.Tuple[str, str]]):
        self.date = time.strptime(date, '%Y-%m-%d')
        self.intervals: typing.List[typing.Tuple[str, str]] = intervals

        self.intervals_: typing.List[typing.Tuple[datetime.datetime, typing.Optional[datetime.datetime]]] = None

    def intervals_as_datetimes(self, *, use_current_time=False):
        if self.intervals_ is None:
            self.intervals_ = []

            for i in self.intervals:
                datetimes = []
                for s in i:
                    if s:
                        parts = list(map(int, s.split(':')))

                        datetimes.append(datetime.datetime(
                            self.date.tm_year,
                            self.date.tm_mon,
                            self.date.tm_mday,
                            *parts
                        ))
                    else:
                        if use_current_time:
                            datetimes.append(datetime.datetime.now())
                        else:
                            datetimes.append(None)

                self.intervals_.append(tuple(datetimes))

        return self.intervals_


class WorktimeProcessor:
    def __init__(self, filename: str):
        self.filename = filename

    def run(self):
        sum_seconds = 0
        required_seconds = 0
        for entry in self._entries():
            required_seconds += 8 * 3600
            (date, seconds, hours, minutes, diff_from_required) = self.sum_of_day(entry)
            sum_seconds += seconds

            self._daily_stat(date, seconds, hours, minutes, required_seconds - sum_seconds)

        self._stat(sum_seconds, required_seconds, required_seconds - sum_seconds)

    def _entries(self):
        def create_tuple(s: str) -> typing.Tuple[str, str]:
            return tuple(s.split('-'))

        with open(self.filename) as f:
            for line in f:
                line = line.strip()
                log_debug(f'Reading line: {line}')
                parts = re.sub("[\t ]+", ' ', line).split()
                log_debug(f'Split: {parts}')
                yield Entry(
                    parts[0],
                    list(map(create_tuple, parts[1:]))
                )

    def sum_of_day(self, entry: Entry) -> typing.Tuple[time.struct_time, int, int, int, int]:
        log_debug(f'Summarize date: {entry.date}')

        def create_dt(s: str) -> datetime.datetime:
            log_debug(f'Create datetime from string: {s}')
            parts = list(map(int, s.split(':')))

            return datetime.datetime(
                entry.date.tm_year,
                entry.date.tm_mon,
                entry.date.tm_mday,
                *parts
            )

        seconds = 0

        for i in entry.intervals:
            interval = tuple(i)
            if not interval[1]:
                interval = (interval[0], datetime.datetime.now().strftime('%H:%M:%S'))

            log_debug(f'Processing interval: {interval}')

            t_from = create_dt(interval[0])
            t_to = create_dt(interval[1])

            diff = t_to - t_from
            seconds += diff.seconds

        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        diff_from_required = 8 * 3600 - seconds

        return (entry.date, seconds, hours, minutes, -diff_from_required)

    def _daily_stat(self, date: time.struct_time, seconds: int, hours: int, minutes: int, diff_from_required: int):
        diff_str = 'remaining' if diff_from_required > 0 else 'overtime'
        diff_from_required = abs(diff_from_required)
        print(time.strftime('%Y-%m-%d', date) +
              f': {hours:02d}:{minutes:02d}  {diff_str:9s}: {diff_from_required // 60 :02d} min')

    def _stat(self, seconds: int, required_seconds: int, diff_from_required: int):
        def _print(title: str, s: int):
            prefix = '-' if s < 0 else ' '
            s = abs(s)
            print(
                f' {title:12s} :  {prefix}{s // 3600 :02d}:{(s % 3600) // 60 :02d}:{s % 60 :02d} ({prefix.strip()}{s} seconds)')

        print('------')
        print('Summary:')
        _print('Actual', seconds)
        _print('Required', required_seconds)
        _print('Difference', diff_from_required)
        print(f' Overtime     :   {"YES" if diff_from_required < 0 else "no"}')


class WorktimeImporter:
    def __init__(self, filename: str, source_filename: str):
        self.filename = filename
        self.source_filename = source_filename
        self.db = create_database_manager(self.filename)

    def run(self):
        for entry in self._entries():
            for (login, logout) in entry.intervals_as_datetimes():
                e = WorktimeEntry()
                e.entry_timestamp = login
                e.is_login = True
                e.save()
                if logout is not None:
                    e = WorktimeEntry()
                    e.entry_timestamp = logout
                    e.is_login = False
                    e.save()

    def _entries(self):
        def create_tuple(s: str) -> typing.Tuple[str, str]:
            return tuple(s.split('-'))

        with open(self.source_filename) as f:
            for line in f:
                line = line.strip()
                log_debug(f'Reading line: {line}')
                parts = re.sub("[\t ]+", ' ', line).split()
                log_debug(f'Split: {parts}')
                yield Entry(
                    parts[0],
                    list(map(create_tuple, parts[1:]))
                )


class WorktimeManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.db = create_database_manager(self.filename)

    def login(self):
        e = WorktimeEntry()
        e.entry_timestamp = datetime.datetime.now()
        e.is_login = True
        e.save()

    def logout(self):
        e = WorktimeEntry()
        e.entry_timestamp = datetime.datetime.now()
        e.is_login = False
        e.save()
