# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import multiprocessing
import os.path

from dewi_logparsers.syslog import ISO8601Parser
from dewi_utils.rrdtool.interval import GraphInterval, GraphIntervalType
from dewi_utils.rrdtool.modifiers import IgnoreLoopbackDisks, SeparateDiskstatsPluginsPerDevice
from dewi_utils.rrdtool.rrdtool import RrdTool
from ..common.base_module_ import BaseModule
from ..config.constants import Mode


class GraphModule(BaseModule):

    def provide(self):
        return 'graph'

    def run(self):
        if not (self._ll_node.mode & Mode.WITH_GRAPHS):
            return

        dir_name = self._root_node.munin_dir
        if os.path.exists(dir_name):
            self._generate(dir_name)

    def _generate(self, dir_name: str):

        modifiers = [
            IgnoreLoopbackDisks(),
            SeparateDiskstatsPluginsPerDevice(),
        ]
        r = RrdTool(dir_name, None, modifiers=modifiers,
                    reference_datetime=ISO8601Parser.to_datetime(self._root_node.bundle.stop_time),
                    intervals=[
                        GraphInterval(GraphIntervalType.HOUR),
                        GraphInterval(GraphIntervalType.DAY),
                        GraphInterval(GraphIntervalType.WEEK),
                        GraphInterval(GraphIntervalType.MONTH),
                        GraphInterval(GraphIntervalType.YEAR),
                    ],
                    parallel_run_count=max(1, multiprocessing.cpu_count() - 1)
                    )
        r.run()
        self._root_node.graphs = r.graph_result
