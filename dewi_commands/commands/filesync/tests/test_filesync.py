# Copyright 2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import io
import unittest.mock

import dewi_core.testcase
from dewi_core.appcontext import ApplicationContext
from dewi_realtime_sync.app import LocalSyncApp, SyncOverKubernetesApp, SyncOverSshApp
from dewi_realtime_sync.filesystem import FilesystemError

from dewi_commands.commands.filesync import KubernetesCommand, LocalCommand, RemoteCommand, SubCommand


class FakeChangeWatcher:
    def __init__(self, errors=None):
        self.errors = errors or []


class FakeApp:
    """A SyncApp that records how it was run instead of watching anything."""

    def __init__(self, errors=None):
        self.change_watcher = FakeChangeWatcher(errors)
        self.timeout = 'not run'

    def run(self, timeout=None):
        self.timeout = timeout


class FakeCommand(SubCommand):
    name = 'fake'
    description = 'A subcommand whose app does not touch the filesystem'

    def __init__(self, app: FakeApp):
        self.app = app
        self.entries = None

    def _create_app(self, ctx, entries):
        self.entries = entries
        return self.app


def _context(**args) -> ApplicationContext:
    ctx = ApplicationContext()
    args.setdefault('entry', ['file.txt'])
    args.setdefault('skip_chmod', False)
    args.setdefault('sync_vcs_directories', None)
    args.setdefault('timeout', None)
    for key, value in args.items():
        ctx.add_arg(key, value)

    return ctx


class TestEntryLoading(dewi_core.testcase.TestCase):
    def test_that_the_entries_are_loaded_and_the_app_is_run(self):
        app = FakeApp()
        command = FakeCommand(app)

        self.assert_equal(0, command.run(_context(entry=['a.txt', 'dir/;/tmp/dir/'])))

        self.assert_equal(['a.txt', 'dir/'], [e.local_path for e in command.entries])
        self.assert_equal(['a.txt', '/tmp/dir/'], [e.target_path for e in command.entries])

    def test_that_the_timeout_is_passed_to_the_app(self):
        app = FakeApp()

        FakeCommand(app).run(_context(timeout=1.5))

        self.assert_equal(1.5, app.timeout)

    def test_that_an_unparsable_entry_is_reported_instead_of_raising(self):
        app = FakeApp()
        stderr = io.StringIO()

        with unittest.mock.patch('sys.stderr', stderr):
            exit_code = FakeCommand(app).run(_context(entry=['a.txt', ';no-source']))

        self.assert_equal(1, exit_code)
        self.assert_in('The source, the first field, must not be empty', stderr.getvalue())
        self.assert_in(';no-source', stderr.getvalue())
        # The app is not even created, let alone run.
        self.assert_equal('not run', app.timeout)


class TestExitCode(dewi_core.testcase.TestCase):
    def test_that_a_run_without_a_failure_succeeds(self):
        self.assert_equal(0, FakeCommand(FakeApp()).run(_context()))

    def test_that_the_failures_collected_during_the_run_are_reported(self):
        app = FakeApp([('/src/a.txt', FilesystemError(['scp', '/src/a.txt'], 1)),
                       ('/src/b.txt', FilesystemError(['scp', '/src/b.txt'], 2))])
        stderr = io.StringIO()

        with unittest.mock.patch('sys.stderr', stderr):
            exit_code = FakeCommand(app).run(_context())

        self.assert_equal(1, exit_code)
        self.assert_in('2 change(s) of 2 path(s) could not be synchronized', stderr.getvalue())
        self.assert_in('/src/a.txt: Command failed with exit code 1', stderr.getvalue())
        self.assert_in('/src/b.txt: Command failed with exit code 2', stderr.getvalue())

    def test_that_a_path_that_failed_repeatedly_is_listed_once(self):
        app = FakeApp([('/src/a.txt', FilesystemError(['scp', 'first'], 1)),
                       ('/src/a.txt', FilesystemError(['scp', 'second'], 1))])
        stderr = io.StringIO()

        with unittest.mock.patch('sys.stderr', stderr):
            exit_code = FakeCommand(app).run(_context())

        self.assert_equal(1, exit_code)
        self.assert_in('2 change(s) of 1 path(s) could not be synchronized', stderr.getvalue())
        self.assert_equal(1, stderr.getvalue().count('/src/a.txt:'))
        self.assert_in('scp first', stderr.getvalue())
        self.assert_not_in('scp second', stderr.getvalue())

    def test_that_an_app_that_was_never_run_has_no_failures(self):
        app = FakeApp()
        app.change_watcher = None

        self.assert_equal(0, FakeCommand(app).run(_context()))


class TestCreatedApps(dewi_core.testcase.TestCase):
    """
    Every subcommand builds its app from the options it registered.

    The apps keep their settings private, which is where the assertions reach:
    a signature that drifts away from the library is exactly what these tests
    are here to catch.
    """

    def _assert_common(self, app):
        self.assert_equal('/tmp/target', app._target_directory)
        self.assert_equal(True, app._sync_vcs_directories)

    def test_local(self):
        ctx = _context(directory='/tmp/src', target_directory='/tmp/target', sync_vcs_directories=True)
        app = LocalCommand()._create_app(ctx, [])

        self.assert_is_instance(app, LocalSyncApp)
        self._assert_common(app)

    def test_remote(self):
        ctx = _context(directory='/tmp/src', target_directory='/tmp/target', sync_vcs_directories=True,
                       user='me', host='example.com', port=2222, skip_host_key_check=True)
        app = RemoteCommand()._create_app(ctx, [])

        self.assert_is_instance(app, SyncOverSshApp)
        self._assert_common(app)

    def test_kubernetes(self):
        ctx = _context(directory='/tmp/src', target_directory='/tmp/target', sync_vcs_directories=True,
                       jobs=4, namespace='ns', pod='pod', container='container')
        app = KubernetesCommand()._create_app(ctx, [])

        self.assert_is_instance(app, SyncOverKubernetesApp)
        self._assert_common(app)
        self.assert_equal(4, app._parallel)
