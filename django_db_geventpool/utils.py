# coding=utf-8

from functools import wraps
from contextlib import contextmanager

from django.core.signals import request_finished


def close_connection(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        finally:
            request_finished.send(sender='greenlet')
    return wrapper


@contextmanager
def nullcontext(enter_result=None):
    yield enter_result
