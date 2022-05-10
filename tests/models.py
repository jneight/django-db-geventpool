# coding=utf-8

from django.db import models


class TestModel(models.Model):
    charfield = models.CharField(max_length=32, blank=True)
    jsonfield = models.JSONField(default=dict)

    def __str__(self):
        return str(self.pk)
