# Copyright 2018-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


import http.server
import socketserver

from dewi_core.appcontext import ApplicationContext
from dewi_core.command import Command
from dewi_core.commandplugin import CommandPlugin
from dewi_core.optioncontext import OptionContext


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "DEWI/1.0"
    c_1K = 1024
    c_1M = c_1K ** 2
    c_10M = 10 * c_1M
    c_1G = c_1K ** 3
    count_ = 40 * c_1M

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/pdf')
        self.send_header('Content-Disposition', 'attachment; filename="random.bin"')
        self.end_headers()

        # not sure about this part below
        with open('/dev/zero', 'rb') as f:
            remaining = self.count_

            while remaining > self.c_10M:
                self.wfile.write(f.read(self.c_10M))
                remaining -= self.c_10M

            self.wfile.write(f.read(remaining))


class Http:
    SUFFIXES = {
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'T': 1024 ** 4,
    }

    def __init__(self, port: int, count: int):
        self.port = port
        self.count = count

    @classmethod
    def convert_count(cls, count: str) -> tuple[bool, int]:
        try:
            count = int(count)
            return True, count
        except ValueError:
            if not count or len(count) < 2:
                return False, 0
            suffix = count[-1].upper()
            value = count[0:-1]
            print(suffix, value)
            try:
                value = int(value)
            except ValueError:
                return False, 0

            if suffix not in cls.SUFFIXES:
                return False, value

            return True, value * cls.SUFFIXES[suffix]

    def run(self):
        print(self.__dict__)
        with socketserver.TCPServer(("", self.port), self.get_handler()) as httpd:
            httpd.serve_forever()

    def get_handler(self):
        Handler.count_ = self.count
        return Handler


class HttpCommand(Command):
    name = 'http'
    # aliases = []
    description = "Streaming HTTP server, /dev/urandom"

    @staticmethod
    def register_arguments(c: OptionContext):
        c.add_option('-p', '--port', type=int, default=8081,
                     help='The port number, default: 8081')
        c.add_option('--count', default='40M',
                     help='Amount of bytes. Can be used the K/M/G suffix. Default: 40M')

    def run(self, ctx: ApplicationContext):
        if ctx.args.port < 1 or ctx.args.port > 65535:
            print(f'Invalid port number: {ctx.args.port}')
            return 1

        success, count = Http.convert_count(ctx.args.count)
        if not success:
            print('Unable to convert count to a number: ' + ctx.args.count)
            return 1

        p = Http(ctx.args.port, count)
        return p.run()


HttpPlugin = CommandPlugin.create(HttpCommand)
