# coding=utf-8

import gevent

from django.utils.unittest import TestCase
from django.db import connection

from .models import TestModel


def test_multiple_connections(count):
    print 'Test {0} starts'.format(count)
    print connection.pool.__dict__
    for x in range(0, 20):
        assert len(TestModel.objects.all()) == 1
    print 'Test {0} ends'.format(count)
    connection.close()


class ModelTest(TestCase):
    def test_model_save(self):

        data = 'testing save'
        obj = TestModel.objects.create(data=data)

        obj2 = TestModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, obj2.data)

    def test_connections(self):
        TestModel.objects.create(data='test')
        greenlets = []

        for x in range(0, 4):
            greenlets.append(gevent.spawn(test_multiple_connections, x))
        gevent.joinall(greenlets)
