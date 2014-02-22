#!/usr/bin/env python
import sys
import django
from django.conf import settings

import gevent.monkey
gevent.monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

if django.get_version().startswith('1.5'):
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
                'OPTIONS': {
                    'autocommit': True,
                    },
            }
        },
        INSTALLED_APPS=(
            'django_db_geventpool',
            'tests',
        ),
        USE_TZ=True,
    )

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)

failures = test_runner.run_tests(['tests', ])
if failures:
    sys.exit(failures)
