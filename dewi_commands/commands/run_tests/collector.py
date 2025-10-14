#  Copyright 2025, Laszlo Attila Toth
#  Distributed under the terms of the GNU Lesser General Public License v3

from dewi_utils.git.git import Git


class Change:
    def __init__(self, kind, filename):
        self._kind = kind
        self._code = kind[0]
        self._filename = filename
        self._orig_filename = filename
        self._percent = -1

    @property
    def kind(self):
        return self._kind

    @property
    def code(self):
        return self._code

    @property
    def filename(self):
        return self._orig_filename

    @property
    def orig_filename(self):
        return self._orig_filename

    @property
    def percent(self):
        return self._percent

    def __str__(self):
        s = f"kind: {self.kind}, code: {self.code}, filename: {self.filename}"
        if self.orig_filename != self.filename:
            s += f", orig_filename: {self.orig_filename}"
        if self.percent != -1:
            s += f", percent: {self.percent}"

        return s

    @classmethod
    def create_from_git_status_line(cls, line: str):
        parts = line.split(' ', 5)[4].split("\t")
        change = cls(parts[0], parts[-1])

        if change.code in ['R', 'C']:  # rename or copy AND edit
            change._percent = int(change.kind[1:])
            change._orig_filename = parts[1]

        return change

    @classmethod
    def create_from_new_file(cls, filename):
        return cls(filename, 'A')


class Collector:
    def __init__(self):
        self._git = Git()

    def collect(self, base_commit: str, /, *, with_untracked_files: bool = True) -> list[Change]:
        output = self._git.run_output(['diff', '--raw', '-M', '-C', base_commit])
        changes = [Change.create_from_git_status_line(line) for line in output.splitlines()]

        if with_untracked_files:
            output = self._git.run_output(['status', '--porcelain', '-M'])

        changes += [Change.create_from_new_file(line[3:]) for line in output.splitlines() if line.startswith('?? ')]

        return changes
