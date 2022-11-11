# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class RebootModule(LogparserBaseModule):
    def get_registration(self):
        return [
            {
                'program': 'cron',
                'message_substring': '(CRON) INFO (Running @reboot jobs)',
                'callback': self.system_reboot
            }
        ]

    def start(self):
        self._reboots = list()

    def system_reboot(self, time: str, program: str, pid: str | None, msg: str):
        self._reboots.append(time)

    def finish(self):
        if len(self._reboots):
            self.add_message(
                Level.WARNING, 'System', 'Reboot',
                "System is rebooted; count='{}'".format(len(self._reboots)),
                details=self._reboots)
