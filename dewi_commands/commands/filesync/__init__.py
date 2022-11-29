# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_realtime_sync.app import LocalSyncApp, SyncOverSshApp, SyncOverKubernetesApp
from dewi_realtime_sync.loader import EntryListLoader


class SubCommand(Command):

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
    def register_sync_entries(c: OptionContext):
        c.add_option(
            '-e', '--entry', required=True, multiple=True,
            help='A file sync entry describing what to synchronize in format'
                 ' source;target;permissions;owner;group;flags'
        )

        c.add_option(
            '-n', '--no-chmod-chown', '--skip-chmod', dest='skip_chmod', is_flag=True, default=False,
            help='Always skip chmod and chown (to run as non-admin on target FS)'
        )


class LocalCommand(SubCommand):
    name = 'local'
    description = 'Synchronize files to another part of local filesystem'

    @classmethod
    def register_arguments(cls, c: OptionContext):
        super().register_directory_args(c)
        super().register_sync_entries(c)

    def run(self, ctx: ApplicationContext) -> int | None:
        entries = EntryListLoader().load_from_string_list(ctx.args.entry, ctx.args.skip_chmod)
        app = LocalSyncApp(ctx.args.directory, ctx.args.target_directory, entries)
        return app.run()


class RemoteCommand(SubCommand):
    name = 'remote'
    description = 'Synchronize files to a remote server using SSH'

    @classmethod
    def register_arguments(cls, c: OptionContext):
        super().register_directory_args(c)
        cls._register_ssh_args(c)
        super().register_sync_entries(c)

    @staticmethod
    def _register_ssh_args(c: OptionContext):
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

    def run(self, ctx: ApplicationContext) -> int | None:
        entries = EntryListLoader().load_from_string_list(ctx.args.entry, ctx.args.skip_chmod)
        app = SyncOverSshApp(ctx.args.directory, ctx.args.target_directory, entries,
                             user=ctx.args.user, host=ctx.args.host, port=ctx.args.port,
                             check_host_key=not ctx.args.skip_host_key_check)
        return app.run()


class KubernetesCommand(SubCommand):
    name = 'kubernetes'
    aliases = ['kube']
    description = 'Synchronize files to a kubernetes pod - container'

    @classmethod
    def register_arguments(cls, c: OptionContext):
        super().register_directory_args(c)
        cls._register_ssh_args(c)
        super().register_sync_entries(c)

    @staticmethod
    def _register_ssh_args(c: OptionContext):
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

    def run(self, ctx: ApplicationContext) -> int | None:
        entries = EntryListLoader().load_from_string_list(ctx.args.entry, ctx.args.skip_chmod)
        app = SyncOverKubernetesApp(ctx.args.directory, ctx.args.target_directory, entries,
                                    parallel=ctx.current_args.jobs,
                                    namespace=ctx.current_args.namespace, pod=ctx.current_args.pod,
                                    container=ctx.current_args.container)
        return app.run()


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
