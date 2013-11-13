django-db-geventpool
====================

Another DB pool using gevent.

*Need Django 1.5.x or Django 1.6.x*



Settings
---------

  * Set `ENGINE` in your database settings to: *'django_db_geventpool.backends.postgresql_psycopg2'*
  * Add `MAX_CONNS` to `OPTIONS` to set the maximun number of connections allowed to database (default=4)

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


Other pools
------------

* `django-db-pool <https://github.com/gmcguire/django-db-pool>`_
* `django-postgresql <https://github.com/kennethreitz/django-postgrespool>`_

