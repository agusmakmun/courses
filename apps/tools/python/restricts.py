# -*- coding: utf-8 -*-
from __future__ import unicode_literals


SAFE_MODULES = ['math', 'random']
MAX_ITER_LEN = 100


def _import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in SAFE_MODULES:
        globals[name] = __import__(name, globals, locals, fromlist, level)
    else:
        raise Exception("Don't you even think about it {0}".format(name))


class MaxCountIter:

    def __init__(self, dataset, max_count):
        self.i = iter(dataset)
        self.left = max_count

    def __iter__(self):
        return self

    def __next__(self):
        if self.left > 0:
            self.left -= 1
            return next(self.i)
        else:
            raise StopIteration()


def _getiter(ob):
    return MaxCountIter(ob, MAX_ITER_LEN)
