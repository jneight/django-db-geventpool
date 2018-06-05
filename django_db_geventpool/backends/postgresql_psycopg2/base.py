# coding=utf-8

import logging
import sys

try:
    import psycopg2.extensions
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

try:
    from gevent.lock import Semaphore
except ImportError:
    from eventlet.semaphore import Semaphore

try:
    from django.db.backends.postgresql_psycopg2.base import CursorWrapper
except ImportError:
    pass

import django
from django.db.backends.postgresql_psycopg2.base import \
    DatabaseWrapper as OriginalDatabaseWrapper
from django.db.backends.signals import connection_created
from django.conf import settings
from django.db.backends.postgresql_psycopg2.base import utc_tzinfo_factory
from django.utils.encoding import force_str

try:
    import psycopg2_pool as psypool
except ImportError:
    import django_db_geventpool.backends.postgresql_psycopg2.psycopg2_pool as psypool
from .creation import DatabaseCreation

logger = logging.getLogger('django.geventpool')

connection_pools = {}
connection_pools_lock = Semaphore(value=1)


class DatabaseWrapperMixin15(object):
    def __init__(self, *args, **kwargs):
        self._pool = None
        super(DatabaseWrapperMixin15, self).__init__(*args, **kwargs)
        self.creation = DatabaseCreation(self)

    @property
    def pool(self):
        if self._pool is not None:
            return self._pool
        connection_pools_lock.acquire()
        if not self.alias in connection_pools:
            self._pool = psypool.PostgresConnectionPool(
                **self.get_connection_params())
            connection_pools[self.alias] = self._pool
        else:
            self._pool = connection_pools[self.alias]
        connection_pools_lock.release()
        return self._pool

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
            self.connection = self.pool.get()
            tz = 'UTC' if settings.USE_TZ else self.settings_dict.get('TIME_ZONE')
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

    def close(self):
        self.validate_thread_sharing()
        if self.connection is None:
            return  # no need to close anything
        try:
            if self.connection.closed:
                logger.warning(
                    'psycopg2 connections will be reset.')
                self.pool.closeall()
                self.connection = None
            else:
                self.pool.put(self.connection)
                self.connection = None
        except:
            # In some cases (database restart, network connection lost etc...)
            # the connection to the database is lost without giving Django a
            # notification. If we don't set self.connection to None, the error
            # will occur a every request.
            self.connection = None
            logger.warning(
                'psycopg2 error while closing the connection.',
                exc_info=sys.exc_info())
            raise

    def closeall(self):
        for pool in connection_pools.values():
            pool.closeall()


class DatabaseWrapperMixin16(object):
    def __init__(self, *args, **kwargs):
        self._pool = None
        super(DatabaseWrapperMixin16, self).__init__(*args, **kwargs)
        self.creation = DatabaseCreation(self)

    @property
    def pool(self):
        if self._pool is not None:
            return self._pool
        connection_pools_lock.acquire()
        if not self.alias in connection_pools:
            self._pool = psypool.PostgresConnectionPool(
                **self.get_connection_params())
            connection_pools[self.alias] = self._pool
        else:
            self._pool = connection_pools[self.alias]
        connection_pools_lock.release()
        return self._pool

    def get_new_connection(self, conn_params):
        if self.connection is None:
            self.connection = self.pool.get()
            self.closed_in_transaction = False
        return self.connection

    def get_connection_params(self):
        conn_params = super(DatabaseWrapperMixin16, self).get_connection_params()
        if 'MAX_CONNS' in self.settings_dict['OPTIONS']:
            conn_params['MAX_CONNS'] = self.settings_dict['OPTIONS']['MAX_CONNS']
        return conn_params

    def close(self):
        self.validate_thread_sharing()
        if self.closed_in_transaction or self.connection is None:
            return  # no need to close anything
        try:
            self._close()
        except:
            # In some cases (database restart, network connection lost etc...)
            # the connection to the database is lost without giving Django a
            # notification. If we don't set self.connection to None, the error
            # will occur at every request.
            self.connection = None
            logger.warning(
                'psycopg2 error while closing the connection.',
                exc_info=sys.exc_info())
            raise
        finally:
            self.set_clean()

    def _close(self):
        if self.connection.closed:
            self.pool.closeall()
        else:
            with self.wrap_database_errors:
                self.pool.put(self.connection)
        self.connection = None

    def closeall(self):
        for pool in connection_pools.values():
            pool.closeall()


class DatabaseWrapperMixin17(object):
    def set_clean(self):
        if self.in_atomic_block:
            self.closed_in_transaction = True
            self.needs_rollback = True


if django.VERSION >= (1, 7):
    class DatabaseWrapperMixin(DatabaseWrapperMixin17, DatabaseWrapperMixin16):
        pass
elif django.VERSION >= (1, 6):
    class DatabaseWrapperMixin(DatabaseWrapperMixin16):
        pass
elif django.VERSION >= (1, 4):
    class DatabaseWrapperMixin(DatabaseWrapperMixin15):
        pass
else:
    raise ImportError("Django version 1.4.x or greater needed")


class DatabaseWrapper(DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pass
