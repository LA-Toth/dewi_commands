# Copyright 2025 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext
from dewi_utils.git.git import Git

from .collector import Collector
from .test_runner import TestRunner


class RunTestsCommand(Command):
    name = 'run-tests'
    aliases = ['runtests']
    description = "Run tests in the current repository against the git changes"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('--ignore-untracked-files', '--ignore-local-files',
                     help='Ignore local files not tracked by git (git status: Untracked files)')
        c.add_option('--test-root', multiple=True,
                     help='Run tests against the given root directory (instead of repo root)')
        c.add_argument('base_commit', nargs=-1, help='Base commit to run the tests against')

    def run(self, ctx: ApplicationContext) -> int | None:
        Git().cd_to_repo_root()
        base_commit = ctx.args.base_commit[0] if len(ctx.args.base_commit) > 0 else None
        git_changes = Collector().collect(base_commit or 'HEAD',
                                          with_untracked_files=not ctx.args.ignore_untracked_files)
        return TestRunner(test_roots=ctx.args.test_root or ['.'], git_changes=git_changes).run()


RunTestsPlugin = CommandPlugin.create(RunTestsCommand)
