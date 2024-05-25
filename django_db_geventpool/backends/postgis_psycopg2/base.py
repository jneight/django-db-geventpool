from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as OriginalDatabaseWrapper,
)

from ..postgresql_psycopg2.base import DatabaseWrapperMixin


class DatabaseWrapper(DatabaseWrapperMixin, OriginalDatabaseWrapper):
    pass
