# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class SshdModule(LogparserBaseModule):
    def get_registration(self):
        return [
            {
                'program': 'sshd',
                'message_substring': 'fatal: No supported key exchange algorithms found [preauth]',
                'callback': self.no_supported_kex_algo
            }
        ]

    def start(self):
        self._kex_failures = list()

    def no_supported_kex_algo(self, time: str, program: str, pid: str | None, msg: str):
        self._kex_failures.append(time)

    def finish(self):
        if len(self._kex_failures):
            self.add_message(
                Level.ALERT,
                'Boot firmware',
                'SSH daemon',
                "An SSH client tries to use unsupported KEX algorithms. count='{}'".format(len(self._kex_failures)),
                hint=[
                    'As it is likely that the SSH client uses old KEX algorithms, SSH client may need to be upgraded.',
                    'Or, check debug log of the client, eg. {code}ssh -vvv{/code}'
                ],
                details=[
                            'Key exchange between the SSH client and the SSH daemon  is not possible.',
                            'Date and program[PID] list follows'
                        ] + self._kex_failures
            )
