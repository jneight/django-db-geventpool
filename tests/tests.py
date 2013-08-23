# coding=utf-8


from django.utils.unittest import TestCase

from .models import TestModel


class ModelTest(TestCase):
    def test_initialization(self):
        obj = TestModel.objects.create()
        self.assertEquals(obj.data, '')

    def test_model_save(self):
        data = 'testing save'
        obj = TestModel(data=data)
        obj.save()

        obj2 = TestModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, obj2.data)
