# this file is a modified version of the psycopg2 used at gevent examples
# to be compatible with django, also checks if
# DB connection is closed and reopen it:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py
import logging
import weakref

logger = logging.getLogger("django.geventpool")

try:
    from gevent import queue
    from gevent.lock import RLock
except ImportError:
    from eventlet import queue
    from ...utils import NullContextRLock as RLock


class DatabaseConnectionPool:
    DBERROR = None

    def __init__(self, maxsize: int = 100, reuse: int = 100):
        # Use a WeakSet here so, even if we fail to discard the connection
        # when it is being closed, or it is closed outside of here, the item
        # will be removed automatically
        self._conns = weakref.WeakSet()
        self.maxsize = maxsize
        self.pool = queue.Queue(maxsize=max(reuse, 1))
        self.lock = RLock()

    @property
    def size(self):
        with self.lock:
            return len(self._conns)

    def get(self):
        try:
            if self.size >= self.maxsize or self.pool.qsize():
                conn = self.pool.get()
            else:
                conn = self.pool.get_nowait()

            try:
                # check connection is still valid
                self.check_usable(conn)
                logger.debug("DB connection reused")
            except self.DBERROR:
                logger.debug("DB connection was closed, creating a new one")
                conn = None
        except queue.Empty:
            conn = None
            logger.debug("DB connection queue empty, creating a new one")

        if conn is None:
            try:
                conn = self.create_connection()
            except Exception:
                raise
            else:
                self._conns.add(conn)

        return conn

    def put(self, item):
        try:
            self.pool.put_nowait(item)
            logger.debug("DB connection returned to the pool")
        except queue.Full:
            item.close()
            self._conns.discard(item)

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
            finally:
                self._conns.discard(conn)

        logger.debug("DB connections all closed")
