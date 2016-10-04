# coding=utf-8

import gevent

try:
    from django.utils.unittest import TestCase
except ImportError:  # removed at 1.9
    from unittest import TestCase

from .models import TestModel

from django_db_geventpool.utils import close_connection


@close_connection
def test_multiple_connections(count):
    print('Test {0} starts'.format(count))
    for x in range(0, 20):
        assert len(TestModel.objects.all()) == 1
    print('Test {0} ends'.format(count))


class ModelTest(TestCase):
    def test_model_save(self):

        data = 'testing save'
        obj = TestModel.objects.create(data=data)

        obj2 = TestModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, obj2.data)

    def test_connections(self):
        TestModel.objects.create(data='test')
        greenlets = []

        for x in range(0, 50):
            greenlets.append(gevent.spawn(test_multiple_connections, x))
        gevent.joinall(greenlets)
