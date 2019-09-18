# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path

import orator
import orator.commands.application

DATABASES = {
    'default': 'sqlite',
    'sqlite': {
        'driver': 'sqlite',
        'database': os.path.expanduser('~/WT.sqlite')
    }
}


def create_database_manager(sqlite_file_path: str) -> orator.DatabaseManager:
    config = {
        'default': 'sqlite',
        'sqlite': {
            'driver': 'sqlite',
            'database': sqlite_file_path,
        }
    }

    db = orator.DatabaseManager(config)
    orator.Model.set_connection_resolver(db)
    return db
