try:
    import psycopg
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("Error loading psycopg3 module: %s" % e)

from django.db.backends.postgresql.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

from .. import base, pool


class PostgresConnectionPool(pool.DatabaseConnectionPool):
    DBERROR = psycopg.DatabaseError

    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop("connect", psycopg.connect)
        self.connection = None
        maxsize = kwargs.pop("MAX_CONNS", 4)
        reuse = kwargs.pop("REUSE_CONNS", maxsize)
        self.args = args
        self.kwargs = kwargs
        self.kwargs["client_encoding"] = "UTF8"
        super().__init__(maxsize, reuse)

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        return conn

    def check_usable(self, connection):
        connection.cursor().execute("SELECT 1")


class DatabaseWrapper(base.DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pool_class = PostgresConnectionPool
    INTRANS = psycopg.pq.TransactionStatus.INTRANS
