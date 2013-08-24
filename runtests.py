#!/usr/bin/env python
import sys
from django.conf import settings

import gevent.monkey
gevent.monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()


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

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)

failures = test_runner.run_tests(['tests', ])
if failures:
    sys.exit(failures)
