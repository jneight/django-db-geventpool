from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

try:
    # try psycopg3
    import psycopg  # noqa
    INTRANS = psycopg.pq.TransactionStatus.INTRANS
    from ..postgresql_psycopg3.base import base, PostgresConnectionPool
except ImportError:
    # fallback to psycopg2
    import psycopg2
    INTRANS = psycopg2.extensions.TRANSACTION_STATUS_INTRANS
    from ..postgresql_psycopg2.base import base, PostgresConnectionPool


class DatabaseWrapper(base.DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pool_class = PostgresConnectionPool
    INTRANS = INTRANS
