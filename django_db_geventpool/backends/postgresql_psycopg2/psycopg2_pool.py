# coding=utf-8

# this file is a modified version of the psycopg2 used at gevent examples
# to be compatible with django, also checks if
# DB connection is closed and reopen it:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py
import logging
import sys
logger = logging.getLogger('django.geventpool')

try:
    from gevent import queue
except ImportError:
    from eventlet import queue

try:
    from psycopg2 import connect, DatabaseError
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

if sys.version_info[0] >= 3:
    integer_types = int,
else:
    import __builtin__
    integer_types = int, __builtin__.long


class DatabaseConnectionPool(object):
    def __init__(self, maxsize=100, wait=False):
        if not isinstance(maxsize, integer_types):
            raise TypeError('Expected integer, got %r' % (maxsize,))

        self.wait = wait
        self.maxsize = maxsize
        self.size = 0
        self.pool = queue.Queue(maxsize=maxsize)

    def get(self):
        try:
            if self.wait and (self.size >= self.maxsize or self.pool.qsize()):
                conn = self.pool.get()
            else:
                conn = self.pool.get_nowait()

            try:
                # check connection is still valid
                self.check_usable(conn)
                logger.debug("DB connection reused")
            except DatabaseError:
                logger.debug("DB connection was closed, creating a new one")
                conn = None
        except queue.Empty:
            conn = None
            logger.debug("DB connection queue empty, creating a new one")

        if conn is None:
            self.size += 1
            try:
                conn = self.create_connection()
            except Exception:
                self.size -= 1
                raise

        return conn

    def put(self, item):
        try:
            self.pool.put_nowait(item)
            logger.debug("DB connection returned")
        except queue.Full:
            item.close()
            self.size -= 1

    def closeall(self):
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
            except queue.Empty:
                continue
            try:
                conn.close()
            except Exception:
                continue

        self.size = 0
        logger.debug("DB connections all closed")


class PostgresConnectionPool(DatabaseConnectionPool):
    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop('connect', connect)
        self.connection = None
        maxsize = kwargs.pop('MAX_CONNS', 4)
        wait = kwargs.pop('WAIT', False)
        self.args = args
        self.kwargs = kwargs
        super(PostgresConnectionPool, self).__init__(maxsize, wait)

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        # set correct encoding
        conn.set_client_encoding('UTF8')
        return conn

    def check_usable(self, connection):
        connection.cursor().execute('SELECT 1')
