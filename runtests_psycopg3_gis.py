#!/usr/bin/env python
import sys
import gevent.monkey

gevent.monkey.patch_all()

import django
from django.conf import settings
from django.test.runner import DiscoverRunner


settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django_db_geventpool.backends.postgis",
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
django.setup()

test_runner = DiscoverRunner(verbosity=2)

failures = test_runner.run_tests(["tests.tests", "tests.tests_gis"])
if failures:
    sys.exit(failures)
