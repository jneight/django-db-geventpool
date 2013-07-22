django-db-geventpool
====================

Another DB pool using gevent.

### Need Django 1.5.x



Settings
---------

  * Set 'ENGINE' in your database settings to: <i>'django_db_geventpoool.backends.postgresql_psycopg2'</i>
  * Add 'MAX_CONNS' to 'OPTIONS' to set the maximun number of connections allowed to database (default=4)
  
```python
DATABASES = {
    'default': {
        'ENGINE': 'django_db_geventpoool.backends.postgresql_psycopg2',
        'NAME': 'db',           # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgres',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
            'autocommit': True,
            'MAX_CONNS': 20
        }
    }
}
```
