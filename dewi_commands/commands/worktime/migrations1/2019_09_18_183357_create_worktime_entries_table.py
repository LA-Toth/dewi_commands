# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from orator.migrations import Migration


class CreateWorktimeEntriesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('worktime_entries') as table:
            table.increments('id')
            table.datetime('entry_timestamp')
            table.boolean('is_login')
            table.timestamps()
            table.soft_deletes()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('worktime_entries')
