# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class ClockModule(LogparserBaseModule):
    def get_registration(self):
        return [
            {
                'program': 'winbindd',
                'message_substring': 'Clock skew too great',
                'callback': self.clock_skew_detected
            },
        ]

    def start(self):
        self._issues = []

    def clock_skew_detected(self, time: str, program: str | None, pid: str, msg: str):
        self._issues.append(f'{time} - {msg}')

    def finish(self):
        if self._issues:
            self.add_message(
                Level.WARNING, 'Winbindd', 'Winbindd',
                "Clock skew detected; count={}".format(len(self._issues)),
                hint=['Check the date/time and the NTP settings.',
                      "It's possible that the other end isn't in synchron."],
                details=self._issues,
            )
