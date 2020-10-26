# coding=utf-8

from django.db import models
from django.contrib.postgres.fields import JSONField


class TestModel(models.Model):
    charfield = models.CharField(max_length=32, blank=True)
    jsonfield = JSONField(default=dict)

    def __str__(self):
        return str(self.pk)
