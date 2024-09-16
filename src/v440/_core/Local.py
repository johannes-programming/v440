from __future__ import annotations

import functools
import types
import typing

import datahold
import scaevola

from . import utils


class Local(datahold.OkayList, scaevola.Scaevola):
    def __le__(self, other):
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    __repr__ = utils.Base.__repr__

    __setattr__ = utils.Base.__setattr__

    def __sorted__(self, /, **kwargs):
        ans = self.copy()
        ans.sort(**kwargs)
        return ans

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
    def data(self, value, /):
        if value is None:
            self._data = list()
            return
        if not utils.isiterable(value):
            value = str(value)
            if value.startswith("+"):
                value = value[1:]
            value = value.replace("_", ".")
            value = value.replace("-", ".")
            value = value.split(".")
        value = [utils.segment(x) for x in value]
        if None in value:
            raise ValueError
        self._data = value

    @data.deleter
    def data(self):
        self._data = list()

    @functools.wraps(datahold.OkayList.sort)
    def sort(self, /, *, key=None, **kwargs):
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, **kwargs)
