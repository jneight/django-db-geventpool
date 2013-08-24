# coding=utf-8

# this file is a modified version of the psycopg2 used at gevent examples
# to be compatible with django, also checks if
# DB connection is closed and reopen it:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py

import logging
logger = logging.getLogger('django')

from gevent.queue import Queue

from psycopg2 import connect


class DatabaseConnectionPool(object):
    def __init__(self, maxsize=4):
        if not isinstance(maxsize, (int, long)):
            raise TypeError('Expected integer, got %r' % (maxsize, ))
        self.maxsize = maxsize
        self.pool = Queue()
        self.size = 0

    def get(self):
        pool = self.pool
        if self.size >= self.maxsize:
            new_connection = pool.get()
            try:
                # check connection is still valid
                new_connection.cursor().execute('SELECT 1')
            except:
                logger.info("DB connection was closed, creating new one")
                try:
                    new_connection.close()
                except:
                    pass
                new_connection = self.create_connection()
            else:
                if not new_connection.autocommit:
                    new_connection.rollback()
        else:
            self.size += 1
            try:
                new_connection = self.create_connection()
            except:
                self.size -= 1
                raise
        return new_connection

    def put(self, connection):
        if connection.closed:
            logger.warning(
                'psycopg2 connections will be reset.')
            self.pool.closeall()
        else:
            logger.debug('deleting, available %s', self.pool.qsize())
            self.pool.put_nowait(connection)
            logger.debug('after, available %s', self.pool.qsize())

    def closeall(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except Exception:
                pass
        self.size = 0


class PostgresConnection(object):
    def __init__(self, pool, connection):
        self._pool = pool
        self._connection = connection

    def __getattr__(self, attr):
        return getattr(self._connection, attr)

    def close(self, *args, **kwargs):
        print 'closed'
        self._pool.put(self._connection)


class PostgresConnectionPool(DatabaseConnectionPool):
    def __init__(self, *args, **kwargs):
        maxsize = kwargs.pop('MAX_CONNS', 4)
        self.args = args
        self.kwargs = kwargs
        DatabaseConnectionPool.__init__(
            self, maxsize)

    def create_connection(self):
        conn = connect(*self.args, **self.kwargs)
        return PostgresConnection(self, conn)
