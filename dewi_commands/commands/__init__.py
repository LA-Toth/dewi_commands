# Copyright 2015-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections.abc

from dewi_core.loader.context import Context
from dewi_core.loader.plugin import Plugin


class ImageHandlerCommandsPlugin(Plugin):
    """Commands to collect / sort / copy / delete images (photos)"""

    def get_dependencies(self) -> collections.abc.Iterable[str]:
        return {
            'dewi_commands.commands.collect_images.ImageCollectorPlugin',
            'dewi_commands.commands.deduplicate_images.ImageDeduplicatorPlugin',
            'dewi_commands.commands.safe_delete_images.SafeEraserPlugin',
            'dewi_commands.commands.select_images.ImageSelectorPlugin',
            'dewi_commands.commands.sort_photos.PhotoSorterPlugin',
        }

    def load(self, c: Context):
        pass


class DeprecatedCommandsPlugin(Plugin):
    """Deprecated commands which are not needed anymore or doesn't work"""

    def get_dependencies(self) -> collections.abc.Iterable[str]:
        return {
            'dewi_commands.commands.fetchcovidhu.FetchCovidHuPlugin',
            'dewi_commands.commands.packt.PacktPlugin',
            'dewi_commands.commands.ssh_ubuntu_windows.SshToUbuntuOnWindowsPlugin',
        }

    def load(self, c: Context):
        pass


class CommandsPlugin(Plugin):
    """Commands of DEWI"""

    def get_dependencies(self) -> collections.abc.Iterable[str]:
        return {
            'dewi_commands.commands.ImageHandlerCommandsPlugin',
            'dewi_commands.commands.awgmm.AwgMmPlugin',
            'dewi_commands.commands.checksums.ChecksumsPlugin',
            'dewi_commands.commands.dice.DicePlugin',
            'dewi_commands.commands.edit.edit.EditPlugin',
            'dewi_commands.commands.filesync.FileSyncPlugin',
            'dewi_commands.commands.find.FindPlugin',
            'dewi_commands.commands.hash.HashPlugin',
            'dewi_commands.commands.http.HttpPlugin',
            'dewi_commands.commands.jsonformatter.JSonFormatterPlugin',
            'dewi_commands.commands.license.LicensePlugin',
            'dewi_commands.commands.lithurgical.LithurgicalPlugin',
            'dewi_commands.commands.primes.PrimesPlugin',
            'dewi_commands.commands.split_zorp_log.SplitZorpLogPlugin',
            'dewi_commands.commands.stripspace.StripSpacePlugin',
            'dewi_commands.commands.sysinfo.SysInfoPlugin',
            'dewi_commands.commands.stocks.StocksPlugin',
            'dewi_commands.commands.worktime.WorktimePlugin',
        }

    def load(self, c: Context):
        pass
