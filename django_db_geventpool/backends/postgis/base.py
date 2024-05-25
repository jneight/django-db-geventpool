from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

try:
    import psycopg  # noqa
    from ..postgresql_psycopg3.base import DatabaseWrapperMixin
except ImportError:
    # fallback to psycopg3
    from ..postgresql_psycopg2.base import DatabaseWrapperMixin


class DatabaseWrapper(DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pass
