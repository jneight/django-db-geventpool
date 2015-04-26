#!/usr/bin/env python
import sys
import gevent.monkey
gevent.monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import django
from django.conf import settings


if django.VERSION < (1,6):
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
                'NAME': 'test',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'OPTIONS': {'autocommit': True},
            }
        },
        INSTALLED_APPS=(
            'django_db_geventpool',
            'tests',
        ),
        USE_TZ=True,
    )
else:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
                'NAME': 'test',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'ATOMIC_REQUESTS': False,
                'CONN_MAX_AGE': 0,
            }
        },
        INSTALLED_APPS=(
            'tests',
            'django_db_geventpool',
        ),
        USE_TZ=True,
    )
    try:
        django.setup()
    except AttributeError:
        pass # not using django 1.7


try:
    from django.test.runner import DiscoverRunner as TestSuiteRunner
except ImportError:  # DiscoverRunner is the preferred one for django > 1.7
    from django.test.simple import DjangoTestSuiteRunner as TestSuiteRunner

test_runner = TestSuiteRunner(verbosity=1)

failures = test_runner.run_tests(['tests', ])
if failures:
    sys.exit(failures)
