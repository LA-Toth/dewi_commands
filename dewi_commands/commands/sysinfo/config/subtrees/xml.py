# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi_dataclass.node import Node


class Xml(Node):
    """
    Holds the parsed XML configuration of a support bundle.

    Part of the original sysinfo implementation, which processed a support
    bundle -- extracted logs, munin graphs, an XML configuration. Kept as an
    almost-working reference implementation.
    """

    def __init__(self):
        # root: an xml.etree.ElementTree.Element, most likely -- the only use
        # is root.find(...), and an ElementTree would serve equally well. Left
        # unannotated on purpose: nothing in this tree assigns it, so the type
        # cannot be verified, and the original annotation named the *module*
        # xml.etree.ElementTree, which is not a type at all.
        self.root = None
