# coding=utf-8

from django.db.backends.postgresql_psycopg2.creation import DatabaseCreation as OriginalDatabaseCreation


class DatabaseCreation(OriginalDatabaseCreation):
    def _destroy_test_db(self, test_database_name, verbosity):
        self.connection.closeall()
        return super(DatabaseCreation, self)._destroy_test_db(test_database_name, verbosity)
    def _create_test_db(self, verbosity, autoclobber):
        self.connection.closeall()
        return super(DatabaseCreation, self)._create_test_db(verbosity, autoclobber)
