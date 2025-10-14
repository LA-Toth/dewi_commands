# Copyright 2025, Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path
import re
import subprocess

from dewi_dataclass.node import Node
from .collector import Change


class TestSuite(Node):
    def __init__(self):
        self.root_dir: str = ''
        self.tests: list[str] = []
        self.command_prefix: list[str] = []

    def command(self):
        if self.root_dir == '.':
            args = self.tests
        else:
            args = [
                x[len(self.root_dir) + 1:] if x.startswith(self.root_dir) else x
                for x in self.tests
            ]

        return self.command_prefix + args

    def run_tests(self):
        print(f'Running tests in {self.root_dir}')
        print(f' --> {", ".join(self.tests)}')
        subprocess.run(self.command(), cwd=self.root_dir, check=True)


class TestRunner:
    def __init__(self, /, test_roots: list[str], git_changes: list[Change]):
        self._test_roots = test_roots
        self._git_changes = git_changes

    def run(self):
        suites = []
        if self._is_ruby_app():
            suites = RubyTestCollector(self._test_roots, self._git_changes).collect()
        self._run_suites(suites)

    def _run_suites(self, suites: list[TestSuite]):
        for suite in suites:
            suite.run_tests()

    def _is_ruby_app(self):
        return self._repo_contains('Gemfile')

    def _repo_contains(self, filename):
        if os.path.exists(filename):
            return True
        all_files = subprocess.check_output(['git', 'ls-files']).decode().splitlines()
        for checked_filename in all_files:
            if checked_filename.endswith('/' + filename):
                return True

        return False


class TestCollector:
    def __init__(self, test_roots: list[str], git_changes: list[Change]):
        self._test_roots = test_roots
        self._git_changes = git_changes

    def collect(self) -> list[TestSuite]:
        suites = self._prepare_suites()

        self._collect_tests_from_changes(suites)
        self._discover_affected_tests(suites)
        self._make_tests_unique(suites)

        return list(suites.values())

    def _make_tests_unique(self, suites: dict[str, TestSuite]):
        for suite in suites.values():
            suite.tests = list(set(suite.tests))

    def _prepare_suites(self) -> dict[str, TestSuite]:
        suites = {}

        for test_root in self._test_roots:
            suite = TestSuite()
            suite.root_dir = test_root
            suites[test_root] = suite
            suite.command_prefix = self._get_command_prefix()
        return suites

    def _get_command_prefix(self) -> str:
        raise NotImplementedError()

    def _collect_tests_from_changes(self, suites: dict[str, TestSuite]):
        raise NotImplementedError()

    def _discover_affected_tests(self, suites: dict[str, TestSuite]):
        raise NotImplementedError()

    def _add_to_test_suites(self, suites: dict[str, TestSuite], filename: str):
        for suite_root_dir in suites:
            if filename.startswith(suite_root_dir) or suite_root_dir == '.':
                suites[suite_root_dir].tests.append(filename)


class RubyTestCollector(TestCollector):
    def __init__(self, test_roots: list[str], git_changes: list[Change]):
        super().__init__(test_roots, git_changes)

    def _get_command_prefix(self) -> list[str]:
        return ['bundle', 'exec', 'rspec']

    def _collect_tests_from_changes(self, suites: dict[str, TestSuite]):
        for change in self._git_changes:
            if change.filename.endswith('_spec.rb'):
                self._add_to_test_suites(suites, change.filename)

    def _discover_affected_tests(self, suites: dict[str, TestSuite]):
        all_files = subprocess.check_output(['git', 'ls-files']).decode().splitlines()

        for change in self._git_changes:
            if change.filename.endswith('.rb') and not change.filename.endswith('_spec.rb'):
                basename = os.path.basename(change.filename[:-len('.rb')])
                for filename in all_files:
                    if re.match(f'^.*/{basename}[^/]*_spec.rb', filename):
                        self._add_to_test_suites(suites, filename)
