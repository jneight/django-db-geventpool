# coding=utf-8

import logging
import sys

import psycopg2.extensions
import psycopg2_pool as psypool
from gevent.coros import Semaphore

from django import get_version
django_version = get_version()

if django_version.startswith('1.5'):
    from django.db.backends.postgresql_psycopg2.base import (
        CursorWrapper, utc_tzinfo_factory)
    from django.utils.encoding import force_str

from django.db.backends.postgresql_psycopg2.base import \
    DatabaseWrapper as OriginalDatabaseWrapper
from django.db.backends.postgresql_psycopg2.creation import \
    DatabaseCreation as OriginalDatabaseCreation
from django.db.backends.signals import connection_created
from django.conf import settings

logger = logging.getLogger(__name__)

connection_pools = {}
connection_pools_lock = Semaphore(value=1)


class DatabaseWrapper15(OriginalDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper15, self).__init__(*args, **kwargs)
        global connection_pools
        global connection_pools_lock
        connection_pools_lock.acquire()
        if not self.alias in connection_pools:
            self.pool = psypool.PostgresConnectionPool(
                **self.get_connection_params())
            connection_pools[self.alias] = self.pool
        else:
            self.pool = connection_pools[self.alias]
        connection_pools_lock.release()

    def get_connection_params(self):
        settings_dict = self.settings_dict
        if not settings_dict['NAME']:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                "settings.DATABASES is improperly configured. "
                "Please supply the NAME value.")
        conn_params = {
            'database': settings_dict['NAME'],
        }
        conn_params.update(settings_dict['OPTIONS'])
        if 'autocommit' in conn_params:
            del conn_params['autocommit']
        if 'isolation_level' in conn_params:
            del conn_params['isolation_level']
        if settings_dict['USER']:
            conn_params['user'] = settings_dict['USER']
        if settings_dict['PASSWORD']:
            conn_params['password'] = force_str(settings_dict['PASSWORD'])
        if settings_dict['HOST']:
            conn_params['host'] = settings_dict['HOST']
        if settings_dict['PORT']:
            conn_params['port'] = settings_dict['PORT']
        if 'MAX_CONNS' in settings_dict['OPTIONS']:
            conn_params['MAX_CONNS'] = settings_dict['OPTIONS']['MAX_CONNS']
        return conn_params

    def _cursor(self):
        if self.connection is None:
            self.connection, new = self.pool.get()
            if new:
                self.connection.set_client_encoding('UTF8')
                tz = 'UTC' if settings.USE_TZ else \
                    self.settings_dict.get('TIME_ZONE')
                if tz:
                    try:
                        get_parameter_status = self.connection.get_parameter_status
                    except AttributeError:
                        # psycopg2 > 2.0.12 doesn't support get_parameter_status
                        conn_tz = None
                    else:
                        conn_tz = get_parameter_status('TimeZone')
                    if conn_tz != tz:
                        self.connection.set_isolation_level(
                            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                        self.connection.cursor().execute(
                            self.ops.set_time_zone_sql(), [tz])
            self.connection.set_isolation_level(self.isolation_level)
            self._get_pg_version()
            connection_created.send(sender=self.__class__, connection=self)
        cursor = self.connection.cursor()
        cursor.tzinfo_factory = utc_tzinfo_factory if settings.USE_TZ else None
        return CursorWrapper(cursor)

    def closeall(self):
        for pool in connection_pools.values():
            pool.closeall()


class DatabaseWrapper16(OriginalDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper16, self).__init__(*args, **kwargs)
        global connection_pools
        global connection_pools_lock
        connection_pools_lock.acquire()
        if not self.alias in connection_pools:
            self.pool = psypool.PostgresConnectionPool(
                **self.get_connection_params())
            connection_pools[self.alias] = self.pool
        else:
            self.pool = connection_pools[self.alias]
        connection_pools_lock.release()

    def get_connection_params(self):
        conn_params = super(DatabaseWrapper16, self).get_connection_params()
        settings_dict = self.settings_dict
        if 'MAX_CONNS' in settings_dict['OPTIONS']:
            conn_params['MAX_CONNS'] = settings_dict['OPTIONS']['MAX_CONNS']
        return conn_params

    def get_new_connection(self, conn_params):
        return self.pool.get()

    def closeall(self):
        for pool in connection_pools.values():
            pool.closeall()


if django_version.startswith('1.5'):
    class DatabaseWrapper(DatabaseWrapper15):
        pass
elif django_version.startswith('1.6'):
    class DatabaseWrapper(DatabaseWrapper16):
        pass
else:
    raise ImportError("Django version 1.5.x or 1.6.x needed")
