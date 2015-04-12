# coding=utf-8

from django_db_geventpool.backends.postgresql_psycopg2.base import DatabaseWrapperMixin

from django.contrib.gis.db.backends.postgis.base import \
    DatabaseWrapper as OriginalDatabaseWrapper

class DatabaseWrapper(DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pass
