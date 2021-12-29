# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import os.path

from dewi_core.logger import log_info
from dewi_core.utils.yaml import load_yaml
from dewi_module_framework.messages import Messages
from dewi_utils.network import NetworkCardVendors
from .config.constants import COMMON_NETWORK_CARD_VENDOR_LIST, Mode
from .config.sysinfoconfig import SysInfoConfig
from .logparsers.module_list import run_parser_modules
from .modules.module_list import run_modules
from .renderer import render


class Processor:
    BASE_PATH = os.path.join(os.path.dirname(__file__), 'templates')
    TEMPLATE_FILENAME = 'index.tpl'

    def __init__(self, log_dir: str,
                 munin_dir: str,
                 output_dir: str,
                 reprocess: bool = False,
                 process_logs: bool = True,
                 process_graphs: bool = True):
        self._log_dir = log_dir
        self._munin_dir = munin_dir
        self._output_dir = output_dir
        self._reprocess = reprocess
        self.generated_yaml_file = os.path.join(self._output_dir, 'result.yml')

        self.config = SysInfoConfig()
        self.root_node = self.config.get_main_node()
        self.ll_node = self.config.get_low_level_details()
        self.root_node.log_dir = self._log_dir
        self.root_node.munin_dir = self._munin_dir

        self.ll_node.oui = NetworkCardVendors(
            os.path.join(os.path.dirname(__file__), 'data', 'oui.yml'),
            COMMON_NETWORK_CARD_VENDOR_LIST,
            enable_debug=True, debug_prefix=' *****>'
        )

        self._set_mode(process_logs, process_graphs)

    def process(self):
        if self._reprocess or not os.path.exists(self.generated_yaml_file):
            messages = Messages()

            log_info('Run modules')
            run_modules(self.config, messages)

            if self.ll_node.mode & Mode.WITH_LOGS:
                log_info('Run logparser modules')
                run_parser_modules(self.config, messages)

            log_info("Postprocessing")

            self.root_node.processed = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')

            messages.print_without_category()
            render(self._output_dir, [self.BASE_PATH, os.path.join(self.BASE_PATH, 'parts')], self.TEMPLATE_FILENAME,
                   self.config, messages, generated=True)
        else:
            self.config.overwrite_config(load_yaml(self.generated_yaml_file))
            render(self._output_dir, [self.BASE_PATH, os.path.join(self.BASE_PATH, 'parts')], self.TEMPLATE_FILENAME,
                   self.config, None, generated=False)

        return 0

    def _set_mode(self, process_logs: bool, process_graphs: bool):
        mode = Mode.NO_MODE
        if process_logs:
            mode |= Mode.WITH_LOGS
        if process_graphs:
            mode |= Mode.WITH_GRAPHS

        self.ll_node.mode = mode
