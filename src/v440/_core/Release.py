from __future__ import annotations

import types
import typing

import datahold

from . import utils


@utils.compclass(list)
class Release(datahold.OkayList):
    def __add__(self, other):
        return type(self)(self._data + list(other))

    def __format__(self, cutoff=None):
        return self.format(cutoff=cutoff)

    def __getitem__(self, key):
        if type(key) is slice:
            return self._getitem_slice(key)
        else:
            return self._getitem_index(key)

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __setitem__(self, key, value):
        if type(key) is slice:
            self._setitem_slice(key, value)
        else:
            self._setitem_index(key, value)

    def __str__(self) -> str:
        return self.format()

    def _getitem_index(self, key):
        key = utils.toindex(key)
        if len(self) <= key:
            return 0
        return self._data[key]

    def _getitem_slice(self, key):
        ans = self._range(key)
        ans = [self._getitem_index(i) for i in ans]
        return ans

    def _range(self, key):
        start = key.start
        stop = key.stop
        step = key.step
        if step is None:
            step = 1
        else:
            step = utils.toindex(step)
            if step == 0:
                raise ValueError
        fwd = step > 0
        if start is None:
            start = 0 if fwd else len(self) - 1
        else:
            start = utils.toindex(start)
        if stop is None:
            stop = len(self) if fwd else -1
        else:
            stop = utils.toindex(stop)
        if start < 0:
            start += len(self)
        if start < 0:
            start = 0 if fwd else -1
        if stop < 0:
            stop += len(self)
        if stop < 0:
            stop = 0 if fwd else -1
        return range(start, stop, step)

    def _setitem_index(self, key, value):
        key = utils.toindex(key)
        value = utils.numeral(value)
        if len(self) > key:
            super().__setitem__(key, value)
            return
        if value == 0:
            return
        self._data.extend([0] * (key - len(self)))
        self._data.append(value)

    def _setitem_slice(self, key, value):
        key = list(self._range(key))
        value = self._todata(value)
        if len(key) != len(value):
            e = "attempt to assign sequence of size %s to extended slice of size %s"
            e %= (len(value), len(key))
            raise ValueError(e)
        for k, v in zip(key, value):
            self._setitem_index(k, v)

    @staticmethod
    def _todata(value):
        return [utils.numeral(x) for x in utils.tolist(value, "v")]

    def bump(self, index=-1, amount=1):
        x = self._getitem_index(index) + amount
        self._setitem_index(index, x)
        if index != -1:
            self.data = self.data[: index + 1]

    @property
    def data(self):
        return list(self._data)

    @data.setter
    @utils.setterdeco
    def data(self, v):
        v = self._todata(v)
        while v and v[-1] == 0:
            v.pop()
        self._data = v

    @data.deleter
    def data(self):
        self._data = []

    def format(self, cutoff=None):
        ans = self[:cutoff]
        if len(ans) == 0:
            ans += [0]
        ans = [str(x) for x in ans]
        ans = ".".join(ans)
        return ans

    @property
    def major(self) -> int:
        return self[0]

    @major.setter
    @utils.setterdeco
    def major(self, value: typing.Any):
        self[0] = value

    @major.deleter
    def major(self):
        del self[0]

    @property
    def micro(self) -> int:
        return self[2]

    @micro.setter
    @utils.setterdeco
    def micro(self, value: typing.Any):
        self[2] = value

    @micro.deleter
    def micro(self):
        del self[2]

    @property
    def minor(self) -> int:
        return self[1]

    @minor.setter
    @utils.setterdeco
    def minor(self, value: typing.Any):
        self[1] = value

    @minor.deleter
    def minor(self):
        del self[1]
