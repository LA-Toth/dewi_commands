# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class KernelModule(LogparserBaseModule):
    def get_registration(self):
        return [
            {
                'program': 'kernel',
                'message_substring': 'blocked for more than 120 seconds',
                'callback': self._blocked_process
            }
        ]

    def start(self):
        self._blocked_process_list = list()

    def _blocked_process(self, time: str, program: str, pid: str | None, msg: str):
        # [16974495.906550] INFO: task httpd:14545 blocked for more than 120 seconds.

        parts = msg.split(' ', 4)
        self._blocked_process_list.append(dict(time=time, program=parts[3]))

    def finish(self):
        if len(self._blocked_process_list):
            self.add_message(
                Level.WARNING, 'System', 'Kernel',
                "Blocked processes; count='{}'".format(len(self._blocked_process_list)),
                details=[
                    f"{x['time']} - {x['program']}" for x in self._blocked_process_list
                ]
            )
