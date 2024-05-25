try:
    import psycopg
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("Error loading psycopg3 module: %s" % e)

from django.db.backends.postgresql.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

from .. import base
from . import pool


class DatabaseWrapper(base.DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pool_class = pool.PostgresConnectionPool
    INTRANS = psycopg.pq.TransactionStatus.INTRANS
