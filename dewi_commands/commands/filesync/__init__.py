# Copyright 2017-2026 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import sys

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_realtime_sync.app import LocalSyncApp, SyncApp, SyncOverKubernetesApp, SyncOverSshApp
from dewi_realtime_sync.filesync_data import FileSyncEntry, FileSyncFlags
from dewi_realtime_sync.loader import EntryFormatError, EntryListLoader


class SubCommand(Command):
    """
    One way of reaching the target filesystem: locally, over SSH or via kubectl.

    The subclasses differ in the options they need and in the app they build;
    loading the entries, running the app and reporting what failed is the same
    for all of them.
    """

    @classmethod
    def register_arguments(cls, c: OptionContext):
        cls.register_directory_args(c)
        cls.register_target_args(c)
        cls.register_sync_entries(c)
        cls.register_sync_options(c)

    @staticmethod
    def register_directory_args(c: OptionContext):
        c.add_option(
            '-d', '--directory', '--source-directory', dest='directory', required=True,
            help='The local root directory which contains files to be synced'
        )
        c.add_option(
            '-t', '--target-directory', dest='target_directory', required=True,
            help='The target root directory, everything will be synced below this directory'
        )

    @staticmethod
    def register_target_args(c: OptionContext):
        """The options of the target filesystem, if it has any."""

    @staticmethod
    def register_sync_entries(c: OptionContext):
        sync_flags = []
        for flag in FileSyncFlags:
            sync_flags.append(f'{flag.value} ({flag.name})')

        c.add_option(
            '-e', '--entry', required=True, multiple=True,
            help=('A file sync entry describing what to synchronize in format'
                  ' source;target;permissions;owner;group;flags.'
                  ' The "target" is optional, by default it is the same as source.'
                  ' When only source (and target) are set, it behaves as: if the source ends with "/",'
                  ' then the directory is recursively copied. If it does not ends with "/", it is a file,'
                  ' copied as-is.'
                  ' Flags: ') + ', '.join(sync_flags)
        )

        c.add_option(
            '-n', '--no-chmod-chown', '--skip-chmod', dest='skip_chmod', is_flag=True, default=False,
            help='Always skip chmod and chown (to run as non-admin on target FS)'
        )

    @staticmethod
    def register_sync_options(c: OptionContext):
        c.add_option(
            '--sync-vcs-directories/--no-sync-vcs-directories', dest='sync_vcs_directories', default=None,
            help='Synchronize .git, .hg and .svn, which are skipped by default.'
                 ' Without either option the DEWI_SYNC_VCS_DIRECTORIES environment variable decides'
        )
        c.add_option(
            '--timeout', dest='timeout', type=float,
            help='Stop after TIMEOUT seconds instead of running until interrupted'
        )

    def run(self, ctx: ApplicationContext) -> int:
        try:
            entries = EntryListLoader().load_from_string_list(ctx.args.entry, ctx.args.skip_chmod)
        except EntryFormatError as e:
            print(f'ERROR: {e}', file=sys.stderr)
            return 1

        app = self._create_app(ctx, entries)
        app.run(ctx.args.timeout)

        return self._exit_code(app)

    def _create_app(self, ctx: ApplicationContext, entries: list[FileSyncEntry]) -> SyncApp:
        raise NotImplementedError()

    @staticmethod
    def _exit_code(app: SyncApp) -> int:
        """
        Non-zero if a change could not be synchronized.

        A failing copy does not stop the synchronization -- the changes that
        follow it are still worth applying, and there is nobody to tell at the
        time it happens -- so the failures are collected as they occur and are
        summarized here, once the run is over.
        """
        change_watcher = app.change_watcher
        errors = change_watcher.errors if change_watcher is not None else []

        if not errors:
            return 0

        # A path can fail more than once: one edit reaches the observer as several
        # changes on some platforms, and a target that cannot be written fails again
        # on every change that follows. What has to be looked at is the paths, so
        # each of them is listed once, with the first failure it had.
        first_error_of_path = {}
        for path, error in errors:
            first_error_of_path.setdefault(path, error)

        print(f'ERROR: {len(errors)} change(s) of {len(first_error_of_path)} path(s) '
              f'could not be synchronized:', file=sys.stderr)
        for path, error in first_error_of_path.items():
            print(f'  {path}: {error}', file=sys.stderr)

        return 1


class LocalCommand(SubCommand):
    name = 'local'
    description = 'Synchronize files to another part of local filesystem'

    def _create_app(self, ctx: ApplicationContext, entries: list[FileSyncEntry]) -> SyncApp:
        return LocalSyncApp(ctx.args.directory, ctx.args.target_directory, entries,
                            sync_vcs_directories=ctx.args.sync_vcs_directories)


class RemoteCommand(SubCommand):
    name = 'remote'
    description = 'Synchronize files to a remote server using SSH'

    @staticmethod
    def register_target_args(c: OptionContext):
        c.add_option(
            '-H', '--host', required=True,
            help='The SSH server\'s host name or IP address'
        )
        c.add_option(
            '-p', '--port', type=int, default=22,
            help='The SSH sever port, default is 22'
        )

        c.add_option(
            '-l', '--login', '-u', '--user', dest='user', required=True,
            help='The username used on the SSH server'
        )

        c.add_option(
            '--skip-host-key-check', is_flag=True, default=False,
            help='Skip check SSH host key - it is insecure, but in trusted environment it is reasonable'
        )

    def _create_app(self, ctx: ApplicationContext, entries: list[FileSyncEntry]) -> SyncApp:
        return SyncOverSshApp(ctx.args.directory, ctx.args.target_directory, entries,
                              user=ctx.args.user, host=ctx.args.host, port=ctx.args.port,
                              check_host_key=not ctx.args.skip_host_key_check,
                              sync_vcs_directories=ctx.args.sync_vcs_directories)


class KubernetesCommand(SubCommand):
    name = 'kubernetes'
    aliases = ['kube']
    description = 'Synchronize files to a kubernetes pod - container'

    @staticmethod
    def register_target_args(c: OptionContext):
        c.add_option(
            '-j', '--jobs', dest='jobs', type=int, default=1,
            help='Sync files in parallel. Default: single threaded. EXPERIMENTAL.'
        )
        c.add_option(
            '-N', '--namespace', required=True,
            help='The kubernetes namespace'
        )
        c.add_option(
            '-p', '--pod', required=True,
            help='The kubernetes pod name'
        )
        c.add_option(
            '-c', '--container', required=True,
            help='The container name in the pod'
        )

    def _create_app(self, ctx: ApplicationContext, entries: list[FileSyncEntry]) -> SyncApp:
        return SyncOverKubernetesApp(ctx.args.directory, ctx.args.target_directory, entries,
                                     parallel=ctx.args.jobs,
                                     namespace=ctx.args.namespace, pod=ctx.args.pod,
                                     container=ctx.args.container,
                                     sync_vcs_directories=ctx.args.sync_vcs_directories)


class FileSyncCommand(Command):
    name = 'filesync'
    aliases = ['dirsync']
    description = "Sync content of a directory to a remote location controlled by mapping rules"
    subcommand_classes = [
        LocalCommand,
        RemoteCommand,
        KubernetesCommand,
    ]


FileSyncPlugin = CommandPlugin.create(FileSyncCommand)
