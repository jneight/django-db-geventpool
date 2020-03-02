# coding=utf-8

from django.db import models


class TestModel(models.Model):
    data = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return str(self.pk)
