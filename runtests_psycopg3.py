#!/usr/bin/env python
import sys
import gevent.monkey
from distutils.version import StrictVersion

gevent.monkey.patch_all()

import django
from django.conf import settings
from django.test.runner import DiscoverRunner


settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django_db_geventpool.backends.postgresql_psycopg3",
            "NAME": "test",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "ATOMIC_REQUESTS": False,
            "CONN_MAX_AGE": 0,
            "HOST": "localhost",
        }
    },
    INSTALLED_APPS=(
        "tests",
        "django_db_geventpool",
    ),
    USE_TZ=True,
)

if StrictVersion(django.get_version()) >= StrictVersion('5.1.0'):
    settings.DATABASES['default']["OPTIONS"] = {"pool": False}

django.setup()

test_runner = DiscoverRunner(verbosity=2)

failures = test_runner.run_tests(["tests.tests"])
if failures:
    sys.exit(failures)
