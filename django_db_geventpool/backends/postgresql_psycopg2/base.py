try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

from django.db.backends.postgresql.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

from .. import base, pool


class PostgresConnectionPool(pool.DatabaseConnectionPool):
    DBERROR = psycopg2.DatabaseError

    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop("connect", psycopg2.connect)
        self.connection = None
        maxsize = kwargs.pop("MAX_CONNS", 4)
        reuse = kwargs.pop("REUSE_CONNS", maxsize)
        self.args = args
        self.kwargs = kwargs
        self.kwargs["client_encoding"] = "UTF8"
        super().__init__(maxsize, reuse)

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        psycopg2.extras.register_default_jsonb(conn_or_curs=conn, loads=lambda x: x)
        return conn

    def check_usable(self, connection):
        connection.cursor().execute("SELECT 1")


class DatabaseWrapper(base.DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pool_class = PostgresConnectionPool
    INTRANS = psycopg2.extensions.TRANSACTION_STATUS_INTRANS
