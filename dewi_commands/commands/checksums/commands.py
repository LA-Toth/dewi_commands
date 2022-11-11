#  Copyright 2022, Laszlo Attila Toth
#  Distributed under the terms of the Apache License, Version 2.0

import collections.abc
import datetime
import os
import sqlite3
import subprocess
import time
from subprocess import CalledProcessError

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.logger import log_error, log_info
from dewi_core.optioncontext import OptionContext


class FileEntry:
    def __init__(self, filename: str, basename: str, uppercase_basename: str, mod_date: int, file_size: int,
                 checksum: str | None = None):
        self.filename = filename
        self.basename = basename
        self.uppercase_basename = uppercase_basename
        self.mod_date = mod_date
        self.size = file_size
        self._mod_date = time.localtime(mod_date)
        self.checksum = checksum

    def __str__(self):
        return str(self.__dict__)


class FileDatabase:
    def __init__(self, filename: str):
        self.filename = filename

        self._conn = sqlite3.connect(self.filename)
        self._ensure_tables()

    def __del__(self):
        self.commit()
        self._conn.close()

    def _ensure_tables(self):
        c = self._conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS file_info (
                            filename text,
                            upper_basename text,
                            filesize INTEGER,
                            mod_date INTEGER,
                            checksum text
                     )''')
        c.execute('''CREATE INDEX IF NOT EXISTS file_info_name_size_date
                            ON file_info
                            (upper_basename, filesize, mod_date)
                     ''')
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS file_info_uniq_entries
                            ON file_info
                            (filename)
                     ''')
        self._conn.commit()

    def query_fileinfo(self, file_entry: FileEntry):
        c = self._conn.execute('SELECT rowid, * FROM file_info'
                               ' WHERE filename=?',
                               [
                                   file_entry.filename,
                               ]
                               )

        return c.fetchone()

    def insert(self, file_entry: FileEntry, checksum: str | None = None):
        self._conn.execute('INSERT INTO file_info'
                           ' (filename, upper_basename, filesize, mod_date, checksum)'
                           ' VALUES (?,?,?,?,?)',
                           [
                               file_entry.filename,
                               file_entry.uppercase_basename,
                               file_entry.size,
                               file_entry.mod_date,
                               checksum or '',
                           ])

    def add_checksum(self, rowid: int, checksum: str):
        self._conn.execute('UPDATE file_info SET checksum = ? WHERE rowid=?', [checksum, rowid])

    def commit(self):
        self._conn.commit()

    def select_all(self, callback: callable):
        c = self._conn.execute('SELECT  * FROM file_info')
        for row in c.fetchall():
            basename = os.path.basename(row[0])
            f = FileEntry(row[0], basename, row[1], row[3], row[2], row[4])
            callback(f)


class Processor:
    COMMIT_AFTER = 30

    def __init__(self, directory: str, db_filename: str, pretend: bool = False):
        self.directory = directory
        self.db_filename = db_filename
        self.pretend = pretend
        self.db = FileDatabase(db_filename)
        self.add_cnt = 0

    def run(self):
        added = False
        skip_cnt = 0
        for x in self._walk():
            from_db = self.db.query_fileinfo(x)
            if not from_db:
                log_info(f'ADD {x.filename}')
                if not self.pretend:
                    if self._insert(x):
                        added = True
                else:
                    added = True
            elif added:
                log_info(f'Skip {x.filename}')
            else:
                skip_cnt += 1
                if skip_cnt % 10000 == 0:
                    log_info("Initial skip of files", count=skip_cnt)

        return 0

    def _walk(self) -> collections.abc.Iterable[FileEntry]:
        os.chdir(self.directory)
        for root, _, files in os.walk('.'):
            for name in files:
                try:
                    full_path = os.path.join(root, name)
                    yield FileEntry(full_path, name, name.upper(), *self._mod_date_and_file_size(full_path))
                except OSError as e:
                    log_error(str(e))

    def _mod_date_and_file_size(self, full_path: str) -> tuple[int, int]:
        f = os.stat(full_path)

        return int(f.st_mtime), f.st_size

    def _checksum(self, filename: str) -> str:
        r = subprocess.check_output(['md5sum', filename])
        return r.decode('UTF-8').split(' ')[0]

    def _insert(self, x: FileEntry):
        try:
            self.db.insert(x, self._checksum(x.filename))
            self._commit()
            return True
        except CalledProcessError as e:
            log_error(str(e))
            return False

    def _commit(self):
        self.add_cnt += 1
        if self.add_cnt >= self.COMMIT_AFTER:
            log_info("...commit")
            self.db.commit()
            self.add_cnt = 0


class CalculateCommand(Command):
    name = 'calculate'
    aliases = ['md5']
    description = "Calculates checksums"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option(
            '-d', '--directory', '--destination-directory', dest='directory', required=True,
            help='Directory to be processed')
        c.add_option(
            '-p', '--pretend', dest='pretend', default=False, is_flag=True,
            help='Pretend only, walk directory tree without checksum')

    def run(self, ctx: ApplicationContext) -> int | None:
        processor = Processor(ctx.current_args.directory, ctx.args.db_filename, ctx.current_args.pretend)
        return processor.run()


class PrintCommand(Command):
    name = 'print'
    description = "Print checksums"

    def run(self, ctx: ApplicationContext) -> int | None:
        db = FileDatabase(ctx.args.db_filename)
        db.select_all(self._print)
        return 0

    def _print(self, f: FileEntry):
        d = datetime.datetime.utcfromtimestamp(f.mod_date).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{f.checksum}  {f.filename}: size: {f.size}, @ {d}")
