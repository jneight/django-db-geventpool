# coding=utf-8

# this file is a modified version of the psycopg2 used at gevent examples
# to be compatible with django, also checks if
# DB connection is closed and reopen it:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py
import logging
logger = logging.getLogger('django')

from gevent.queue import Queue

from psycopg2 import connect, DatabaseError


class DatabaseConnectionPool(object):
    def __init__(self, maxsize=100):
        if not isinstance(maxsize, (int, long)):
            raise TypeError('Expected integer, got %r' % (maxsize, ))
        self.maxsize = maxsize
        self.pool = Queue()
        self.size = 0

    def get(self):
        pool = self.pool
        if self.size >= self.maxsize or pool.qsize():
            new_item = pool.get()
            try:
                # check connection is still valid
                self.check_usable(new_item)
                logger.debug("DB connection reused")
            except DatabaseError:
                logger.debug("DB connection was closed, creating new one")
                new_item = self.create_connection()
            return new_item
        else:
            self.size += 1
            try:
                new_item = self.create_connection()
                logger.debug("DB connection created")
            except:
                self.size -= 1
                raise
            return new_item

    def put(self, item):
        self.pool.put(item, timeout=2)

    def closeall(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except Exception:
                pass
        self.size = 0


class PostgresConnectionPool(DatabaseConnectionPool):
    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop('connect', connect)
        self.connection = None
        maxsize = kwargs.pop('MAX_CONNS', 4)
        self.args = args
        self.kwargs = kwargs
        DatabaseConnectionPool.__init__(
            self, maxsize)

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        # set correct encoding
        conn.set_client_encoding('UTF8')
        return conn

    def check_usable(self, connection):
        connection.cursor().execute('SELECT 1')

