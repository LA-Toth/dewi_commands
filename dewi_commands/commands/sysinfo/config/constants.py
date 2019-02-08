# Copyright 2017-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import enum

COMMON_NETWORK_CARD_VENDOR_LIST = {
    '000569': 'VMware, Inc.',
    '000C29': 'VMware, Inc.',
    '001C14': 'VMware, Inc.',
    '005056': 'VMware, Inc.',
    '00155D': 'Microsoft Corporation',
    '14C213': 'Apple, Inc.',
    '14D00D': 'Apple, Inc.',
    '182032': 'Apple, Inc.',
    '183451': 'Apple, Inc.',
    '186590': 'Apple, Inc.',
    '18810E': 'Apple, Inc.',
    '189EFC': 'Apple, Inc.',
    '18AF61': 'Apple, Inc.',
    '18AF8F': 'Apple, Inc.',
}


class Mode(enum.Flag):
    NO_MODE = 0
    WITH_LOGS = enum.auto()
    WITH_GRAPHS = enum.auto()
