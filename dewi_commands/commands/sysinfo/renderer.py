# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import os
import shutil

import yaml

from dewi_module_framework.messages import Messages
from dewi_utils.render import TemplateRenderer
from dewi_utils.rrdtool.writer import GraphResult
from .config.sysinfoconfig import SysInfoConfig


def render(output_dir: str, base_path: str | list[str], template_path: str,
           config: SysInfoConfig, messages: Messages | None,
           *,
           generated: bool = True):
    os.makedirs(output_dir, 0o755, exist_ok=True)

    if generated:
        _prepare_config(config, messages)

        with open(os.path.join(output_dir, 'result.yml'), 'w') as f:
            config.dump(f, ignore=['_ll', 'xml'])

    _copy_assets(output_dir)
    _render_graphs(config.get_main_node().graphs, os.path.join(output_dir, 'graphs'))
    _transform_graphs(config)

    config.get_main_node().generated = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')

    r = TemplateRenderer(base_path)
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(r.render(template_path, config.get_config()))


def _copy_assets(dir_name):
    asset_dst_dir = os.path.join(dir_name, 'assets')
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    source_dir = os.path.join(data_dir, 'node_modules')
    with open(os.path.join(data_dir, 'assets.yaml')) as f:
        assets_conf = yaml.load(f)
    for module in assets_conf:
        mod_dir = os.path.join(asset_dst_dir, module)

        if 'dir' in assets_conf[module]:
            if not os.path.exists(mod_dir):
                shutil.copytree(os.path.join(source_dir, assets_conf[module]['dir']), mod_dir)
        else:
            if not os.path.exists(mod_dir):
                os.makedirs(mod_dir)

            for srcdir in assets_conf[module]['dirs']:
                full_srcdir = os.path.join(source_dir, srcdir)
                full_dstdir = os.path.join(mod_dir, os.path.basename(full_srcdir))
                if not os.path.exists(full_dstdir):
                    shutil.copytree(full_srcdir, full_dstdir)


def _render_graphs(graphs: GraphResult, directory: str):
    os.makedirs(directory, exist_ok=True)
    for graph in graphs.graphs:
        filename = os.path.join(directory,
                                f'{graph.category}-{graph.short_name}-{graph.interval_type.lower()}.png')

        with open(filename, 'wb') as f:
            f.write(graph.image)


def _transform_graphs(config: SysInfoConfig):
    graphs = config.get_main_node().graphs.graphs
    graphs_new = dict(categories_=list(), g=dict())

    for graph in graphs:
        graph.category = graph.category.capitalize()

        if graph.category not in graphs_new['g']:
            graphs_new['g'][graph.category] = dict(short_names=list(), s=dict())

        if graph.short_name not in graphs_new['g'][graph.category]['s']:
            graphs_new['g'][graph.category]['s'][graph.short_name] = dict(title=graph.title, intervals=dict())

        graphs_new['g'][graph.category]['s'][graph.short_name]['intervals'][graph.interval_type.lower()] = graph
        graph.filename = f'{graph.category}-{graph.short_name}-{graph.interval_type.lower()}.png'

    graphs_new['categories_'] = sorted(list(graphs_new['g'].keys()))

    for category in graphs_new['categories_']:
        graphs_new['g'][category]['short_names_'] = sorted(list(graphs_new['g'][category]['s'].keys()))

    config.set('graphs', graphs_new)


def _prepare_config(config: SysInfoConfig, messages: Messages | None):
    config.set('alerts', messages.alerts)
    config.set('warnings', messages.warnings)
