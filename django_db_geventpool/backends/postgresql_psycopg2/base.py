try:
    import psycopg2.extensions
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

from django.db.backends.postgresql.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

from .. import base
from . import psycopg2_pool


class DatabaseWrapper(base.DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pool_class = psycopg2_pool.PostgresConnectionPool
    INTRANS = psycopg2.extensions.TRANSACTION_STATUS_INTRANS
