# this file is a copy of:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py
import sys
import contextlib
import logging
logger = logging.getLogger('django')

import gevent
from gevent.queue import Queue

from psycopg2 import OperationalError, connect

# we are already using psycogreen, this isn't needed
# from gevent.socket import wait_read, wait_write
# from psycopg2 import extensions
# def gevent_wait_callback(conn, timeout=None):
#     """A wait callback useful to allow gevent to work with Psycopg."""
#     while 1:
#         state = conn.poll()
#         if state == extensions.POLL_OK:
#             break
#         elif state == extensions.POLL_READ:
#             wait_read(conn.fileno(), timeout=timeout)
#         elif state == extensions.POLL_WRITE:
#             wait_write(conn.fileno(), timeout=timeout)
#         else:
#             raise OperationalError(
#                 "Bad result from poll: %r" % state)
# extensions.set_wait_callback(gevent_wait_callback)


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
                new_item.cursor().execute('SELECT NOW() AS testing')
            except:
                logger.info("DB connection was closed, creating new one")
                try:
                    new_item.close()
                except:
                    pass
                new_item = self.create_connection()
            return new_item
        else:
            self.size += 1
            try:
                new_item = self.create_connection()
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

    @contextlib.contextmanager
    def connection(self, isolation_level=None):
        conn = self.get()
        try:
            if isolation_level is not None:
                if conn.isolation_level == isolation_level:
                    isolation_level = None
                else:
                    conn.set_isolation_level(isolation_level)
                conn.set_client_encoding('UTF8')
            yield conn
        except:
            if conn.closed:
                conn = None
                self.closeall()
            else:
                conn = self._rollback(conn)
            raise
        else:
            if conn.closed:
                raise OperationalError(
                    "Cannot commit because connection was closed: %r" % (conn, ))
            conn.commit()
        finally:
            if conn is not None and not conn.closed:
                if isolation_level is not None:
                    conn.set_isolation_level(isolation_level)
                self.put(conn)

    @contextlib.contextmanager
    def cursor(self, *args, **kwargs):
        isolation_level = kwargs.pop('isolation_level', None)
        with self.connection(isolation_level) as conn:
            yield conn.cursor(*args, **kwargs)

    def _rollback(self, conn):
        try:
            conn.rollback()
        except:
            gevent.get_hub().handle_error(conn, *sys.exc_info())
            return
        return conn

    def execute(self, *args, **kwargs):
        with self.cursor(**kwargs) as cursor:
            cursor.execute(*args)
            return cursor.rowcount

    def fetchone(self, *args, **kwargs):
        with self.cursor(**kwargs) as cursor:
            cursor.execute(*args)
            return cursor.fetchone()

    def fetchall(self, *args, **kwargs):
        with self.cursor(**kwargs) as cursor:
            cursor.execute(*args)
            return cursor.fetchall()

    def fetchiter(self, *args, **kwargs):
        with self.cursor(**kwargs) as cursor:
            cursor.execute(*args)
            while True:
                items = cursor.fetchmany()
                if not items:
                    break
                for item in items:
                    yield item


class PostgresConnectionPool(DatabaseConnectionPool):
    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop('connect', connect)
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
