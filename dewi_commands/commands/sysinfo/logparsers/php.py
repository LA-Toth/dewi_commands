import typing

from dewi_module_framework.messages import Level
from ..common.base_module_ import LogparserBaseModule


class PhpModule(LogparserBaseModule):

    def get_registration(self):
        return [
            {
                'message_substring': 'PHP Fatal error:',
                'callback': self.fatal_error
            }
        ]

    def start(self):
        self._events = list()

    def fatal_error(self, time: str, program: str, pid: typing.Optional[str], msg: str):
        self._events.append(f'{time} - {msg}')

    def finish(self):
        if self._events:
            self.add_message(
                Level.ALERT, 'PHP', 'PHP',
                "PHP fatal errors found; count='{}'".format(len(self._events)),
                details=self._events)
