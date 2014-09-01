django-db-geventpool
====================

.. image:: https://travis-ci.org/jneight/django-db-geventpool.png?branch=master  
   :target: https://travis-ci.org/jneight/django-db-geventpool


Another DB pool using gevent for PostgreSQL DB.

*Need Django 1.5.x or newer (check settings for django >= 1.6)*


Patch psycopg2
--------------

Before using the pool, psycopg2 must be patched with psycogreen, if you are using `gunicorn webserver <http://www.gunicorn.org/>`_,
a good place is the `post_fork()` function at the config file

.. code:: python

   from psycogreen.gevent import patch_psycopg

   def post_fork(server, worker):
       patch_psycopg()
       worker.log_info("Made Psycopg2 Green")


Settings
---------


  * Set `ENGINE` in your database settings to: *'django_db_geventpool.backends.postgresql_psycopg2'*
  * Or for postgis: *'django_db_geventpool.backends.postgis'*
  * Add `MAX_CONNS` to `OPTIONS` to set the maximun number of connections allowed to database (default=4)
  * If using django 1.6 or newer, add `CONN_MAX_AGE: 0` to settings to disable default django persistent connection feature. And read below note if you are manually spawning greenlets 

.. code:: python

    # for django 1.5.x
    DATABASES = {
        'default': {
            'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
            'NAME': 'db',           # Or path to database file if using sqlite3.
            'USER': 'postgres',                      # Not used with sqlite3.
            'PASSWORD': 'postgres',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            'OPTIONS': {
                'MAX_CONNS': 20
            }
        }
    }

    # for django 1.6 and newer version, CONN_MAX_AGE must be set to 0, or connections will never go back to the pool
    DATABASES = {
        'default': {
            'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
            'NAME': 'db',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '',
            'PORT': '',
            'ATOMIC_REQUESTS': False,
            'AUTOCOMMIT': True,
            'CONN_MAX_AGE': 0,
            'OPTIONS': {
                'MAX_CONNS': 20
            }
        }
    }

Using Django 1.6+ ORM when not serving requests
____________

On If you are using django 1.6+ with the celery gevent pool, or have code that manually spawn greenlets it will not be sufficient to set CONN_MAX_AGE to 0.
Django only checks for long-live connections when finishing a requests - So if you manually spawn a greenlet (or have celery spawning one) it's connections will
not get cleaned up but live one for the server to timeout. In production this can cause quite some open connections and while developing it can hamper your tests cases.

To solve it make sure that each greenlet either sends the django.core.signals.request_finished signal or calls django.db.close_old_connections() right before it ends

The decorator method is preferred, but the other alternatives are also valid.

.. code:: python

   from django_db_geventpool.utils import close_connection

   @close_connection
   def greenlet_worker()
        ...

or 

.. code:: python

   from django.core.signals import request_finished
   def greenlet_worker():
      ...
      request_finished.send(sender="greenlet")

or

.. code:: python

   from django.db import close_old_connections
   def greenlet_worker():
      ...
      close_old_connections()


Other pools
------------

* `django-db-pool <https://github.com/gmcguire/django-db-pool>`_
* `django-postgresql <https://github.com/kennethreitz/django-postgrespool>`_

