from psycopg2 import connect, DatabaseError
import psycopg2.extras

from .. import pool


class PostgresConnectionPool(pool.DatabaseConnectionPool):
    DBERROR = DatabaseError

    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop("connect", connect)
        self.connection = None
        maxsize = kwargs.pop("MAX_CONNS", 4)
        reuse = kwargs.pop("REUSE_CONNS", maxsize)
        self.args = args
        self.kwargs = kwargs
        super().__init__(maxsize, reuse)

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        # set correct encoding
        conn.set_client_encoding("UTF8")
        psycopg2.extras.register_default_jsonb(conn_or_curs=conn, loads=lambda x: x)
        return conn

    def check_usable(self, connection):
        connection.cursor().execute("SELECT 1")
