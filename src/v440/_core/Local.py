from __future__ import annotations

import functools
import types
import typing

import datahold

from . import utils


class Local(datahold.OkayList):
    def __add__(self, other):
        return type(self)(self._data + list(other))

    def __le__(self, other):
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __str__(self) -> str:
        return ".".join(str(x) for x in self)

    def _cmpkey(self):
        return [self._sortkey(x) for x in self]

    @staticmethod
    def _sortkey(value):
        return type(value) is int, value

    @property
    def data(self, /):
        return list(self._data)

    @data.setter
    @utils.setterdeco
    def data(self, data, /):
        self._data = utils.todata(data, "+")

    @data.deleter
    def data(self):
        self._data = []

    @functools.wraps(datahold.OkayList.extend)
    def extend(self, other, /):
        self._data += type(self)(other)._data

    @functools.wraps(datahold.OkayList.sort)
    def sort(self, key=None, **kwargs):
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, **kwargs)
