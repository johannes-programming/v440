from __future__ import annotations

import functools
import string
import types
import typing

import datahold
import scaevola

from . import utils


class Release(datahold.OkayList, scaevola.Scaevola):
    def __add__(self, other, /):
        other = type(self)(other)
        ans = self.copy()
        ans._data += other._data
        return ans

    def __delitem__(self, key):
        if type(key) is slice:
            self._delitem_slice(key)
        else:
            self._delitem_index(key)

    def __getitem__(self, key):
        if type(key) is slice:
            return self._getitem_slice(key)
        else:
            return self._getitem_index(key)

    def __iadd__(self, other, /):
        self._data += type(self)(other)._data

    @typing.overload
    def __init__(self, /, data=[]): ...
    @typing.overload
    def __init__(self, /, major=0, minor=0, micro=0): ...
    def __init__(self, *args, **kwargs):
        self._init(*args, **kwargs)(*args, **kwargs)

    __repr__ = utils.Base.__repr__

    __setattr__ = utils.Base.__setattr__

    def __setitem__(self, key, value):
        if type(key) is slice:
            self._setitem_slice(key, value)
        else:
            self._setitem_index(key, value)

    def __str__(self) -> str:
        return self.format()

    def _delitem_index(self, key):
        key = utils.toindex(key)
        if key < len(self):
            del self._data[key]

    def _delitem_slice(self, key):
        key = utils.torange(key, len(self))
        key = [k for k in key if k < len(self)]
        key.sort(reverse=True)
        for k in key:
            del self._data[k]

    def _getitem_index(self, key):
        key = utils.toindex(key)
        if key < len(self):
            return self._data[key]
        else:
            return 0

    def _getitem_slice(self, key):
        key = utils.torange(key, len(self))
        ans = [self._getitem_index(i) for i in key]
        return ans

    def _init(self, *args, **kwargs):
        if "data" in kwargs.keys():
            return self._init_data
        if len(kwargs):
            return self._init_items
        if len(args) < 2:
            return self._init_data
        else:
            return self._init_items

    def _init_data(self, /, data=[]):
        self.data = data

    def _init_items(self, /, major=0, minor=0, micro=0):
        self.data = []
        self.major = major
        self.minor = minor
        self.micro = micro

    def _setitem_index(self, key, value):
        key = utils.toindex(key)
        value = utils.numeral(value)
        length = len(self)
        if length > key:
            self._data[key] = value
            return
        if value == 0:
            return
        self._data.extend([0] * (key - length))
        self._data.append(value)

    def _setitem_slice(self, key, value):
        key = utils.torange(key, len(self))
        if key.step == 1:
            self._setitem_slice_simple(key, value)
        else:
            self._setitem_slice_complex(key, value)

    def _setitem_slice_simple(self, key, value):
        data = self.data
        ext = max(0, key.start - len(data))
        data += ext * [0]
        value = self._tolist(value, slicing="always")
        data = data[: key.start] + value + data[key.stop :]
        while len(data) and not data[-1]:
            data.pop()
        self._data = data
        return

    def _setitem_slice_complex(self, key: range, value):
        key = list(key)
        value = self._tolist(value, slicing=len(key))
        if len(key) != len(value):
            e = "attempt to assign sequence of size %s to extended slice of size %s"
            e %= (len(value), len(key))
            raise ValueError(e)
        maximum = max(*key)
        ext = max(0, maximum + 1 - len(self))
        data = self.data
        data += [0] * ext
        for k, v in zip(key, value):
            data[k] = v
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @staticmethod
    def _tolist(value, *, slicing):
        if isinstance(value, int):
            return [utils.numeral(value)]
        elif isinstance(value, str):
            pass
        elif utils.isiterable(value):
            value = [utils.numeral(x) for x in value]
            return value
        else:
            slicing = "never"
        value = str(value)
        if value == "":
            return list()
        if "" == value.strip(string.digits) and slicing in (len(value), "always"):
            return [int(x) for x in value]
        value = value.lower().strip()
        value = value.replace("_", ".")
        value = value.replace("-", ".")
        if value.startswith("v") or value.startswith("."):
            value = value[1:]
        value = value.split(".")
        if "" in value:
            raise ValueError
        value = [utils.numeral(x) for x in value]
        return value

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
        v = self._tolist(v, slicing="always")
        while v and v[-1] == 0:
            v.pop()
        self._data = v

    @data.deleter
    def data(self):
        self._data = []

    def extend(self, other, /):
        self += other

    def format(self, cutoff=None):
        format_spec = str(cutoff) if cutoff else ""
        i = int(format_spec) if format_spec else None
        ans = self[:i]
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
