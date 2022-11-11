# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class HaModule(LogparserBaseModule):
    HB_MSG_PARTS = [
        'info: mach_down takeover complete',
        'info: Heartbeat shutdown in progress.'
    ]

    def get_registration(self):
        return [
            # {'program': 'cl_status', 'callback': self.cl_status},
            {'program': 'heartbeat', 'callback': self.heartbeat}
        ]

    def start(self):
        self._hb_issues = list()

    def finish(self):
        self.set('ha.heartbeat.count', len(self._hb_issues))

        if len(self._hb_issues):
            self.add_message(Level.WARNING, 'HA', 'HA', 'Check HA messages.',
                             details=[
                                 f"{x['time']} - pid: {x['pid']}: {x['msg']}"
                                 for x in self._hb_issues
                             ])

    def cl_status(self, time: str, program: str, pid: str | None, msg: str):
        # self.add_message(Level.WARNING, 'HA', 'HA', 'CL:' + msg)
        pass

    def heartbeat(self, time: str, program: str, pid: str, msg: str):
        for part in self.HB_MSG_PARTS:
            if part in msg:
                self._hb_issues.append(
                    dict(
                        time=time,
                        pid=pid,
                        msg=msg[:-1]
                    )
                )
