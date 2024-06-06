import gevent

from django.test import TestCase
from django_db_geventpool.utils import close_connection

from .models import TestModel


@close_connection
def test_multiple_connections(count):
    print("Test {0} starts".format(count))
    for x in range(0, 20):
        assert not TestModel.objects.exists()
    print("Test {0} ends".format(count))


class ModelTest(TestCase):
    databases = {"default"}

    def test_model_save(self):
        data = {
            "charfield": "testing save",
            "jsonfield": {"test": "value"},
        }
        pk = TestModel.objects.create(**data).pk

        obj = TestModel.objects.get(pk=pk)
        for key in data.keys():
            self.assertEqual(data[key], getattr(obj, key))

    def test_connections(self):
        greenlets = []

        for x in range(0, 50):
            greenlets.append(gevent.spawn(test_multiple_connections, x))
        gevent.joinall(greenlets, raise_error=True)
