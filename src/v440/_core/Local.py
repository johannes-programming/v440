from __future__ import annotations

import functools
import types
import typing

import datahold
import scaevola

from . import utils


class Local(datahold.OkayList, scaevola.Scaevola):
    def __ge__(self, other):
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return other <= self
        return self.data >= other

    def __le__(self, other):
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return self._cmpkey() <= other._cmpkey()
        return self.data <= other

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

    @utils.proprietary
    class data:
        def getter(self, /):
            return list(self._data)

        @utils.digest
        class setter:
            def byInt(self, value):
                self._data = [value]

            def byList(self, value):
                value = [utils.segment(x) for x in value]
                if None in value:
                    raise ValueError
                self._data = value

            def byNone(self):
                self._data = list()

            def byStr(self, value):
                if value.startswith("+"):
                    value = value[1:]
                value = value.replace("_", ".")
                value = value.replace("-", ".")
                value = value.split(".")
                value = [utils.segment(x) for x in value]
                if None in value:
                    raise ValueError
                self._data = value

    @functools.wraps(datahold.OkayList.sort)
    def sort(self, /, *, key=None, **kwargs):
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, **kwargs)
