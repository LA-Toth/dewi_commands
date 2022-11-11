# Copyright 2019-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import re
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dewi_commands.commands.worktime.models.base import Base
from dewi_commands.commands.worktime.models.worktime_entry import WorktimeEntry
from dewi_core.logger import log_debug


class Entry:
    def __init__(self, date: str, intervals: list[tuple[str, str]]):
        self.date = time.strptime(date, '%Y-%m-%d')
        self.intervals: list[tuple[str, str]] = intervals

        self.intervals_: list[tuple[datetime.datetime, datetime.datetime | None]] = None

    def intervals_as_datetimes(self, *, use_current_time=False) -> \
            list[tuple[datetime.datetime, datetime.datetime | None]]:
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
    def __init__(self, filename: str, *, today_only: bool = False):
        self.filename = filename
        self.today_only = today_only

    def run(self):
        today = datetime.date.today()
        today = (today.year, today.month, today.day)

        sum_seconds = 0
        required_seconds = 0

        last_month = (None, None)

        for entry in self._entries():
            (date, seconds, hours, minutes, diff_from_required) = self.sum_of_day(entry)

            current_month = (date.tm_year, date.tm_mon)
            if last_month != current_month:
                if last_month[0] is not None and not self.today_only:
                    self._stat(sum_seconds, required_seconds, required_seconds - sum_seconds, last=False)

                sum_seconds = 0
                required_seconds = 0
                last_month = current_month

            required_seconds += 8 * 3600
            sum_seconds += seconds

            if not self.today_only or (date.tm_year, date.tm_mon, date.tm_mday) == today:
                self._daily_stat(date, seconds, hours, minutes, required_seconds - sum_seconds)

        self._stat(sum_seconds, required_seconds, required_seconds - sum_seconds)

    def _entries(self):
        def create_tuple(s: str) -> tuple[str, str]:
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

    def sum_of_day(self, entry: Entry) -> tuple[time.struct_time, int, int, int, int]:
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

    def _stat(self, seconds: int, required_seconds: int, diff_from_required: int, *, last: bool = True):
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
        if diff_from_required > 0:
            estimated_end = datetime.datetime.now() + datetime.timedelta(seconds=diff_from_required)
            print(f' Estimated end:   {estimated_end.strftime("%Y-%m-%d %T")}')

        if not last:
            print('------\n')


class DatabaseUser:
    def __init__(self, filename: str):
        self.filename = filename
        self.engine = create_engine('sqlite+pysqlite:///' + self.filename)
        self.session = sessionmaker(bind=self.engine)()

    def create_entry(self, event_at: datetime.datetime, *, is_login: bool) -> WorktimeEntry:
        e = WorktimeEntry()
        e.event_at = event_at
        e.is_login = is_login
        e.init_fields()
        return e

    def create_login_entry(self, event_at: datetime.datetime) -> WorktimeEntry:
        return self.create_entry(event_at, is_login=True)

    def create_logout_entry(self, event_at: datetime.datetime) -> WorktimeEntry:
        return self.create_entry(event_at, is_login=False)


class WorktimeImporter(DatabaseUser):
    def __init__(self, filename: str, source_filename: str):
        super().__init__(filename)
        self.source_filename = source_filename

    def run(self):
        Base.metadata.create_all(self.engine)
        for entry in self._entries():
            for (login, logout) in entry.intervals_as_datetimes():
                self.session.add(self.create_login_entry(login))
                if logout is not None:
                    self.session.add(self.create_login_entry(logout))

        self.session.commit()

    def _entries(self):
        def create_tuple(s: str) -> tuple[str, str]:
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


class WorktimeManager(DatabaseUser):
    def __init__(self, filename: str):
        super().__init__(filename)

    def login(self):
        self.session.add(self.create_login_entry(datetime.datetime.now()))
        self.session.commit()

    def logout(self):
        self.session.add(self.create_logout_entry(datetime.datetime.now()))
        self.session.commit()
