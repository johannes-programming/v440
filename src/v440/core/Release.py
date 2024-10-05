from __future__ import annotations

import operator
import string
from typing import *

from keyalias import keyalias
from overloadable import overloadable

from v440._utils import utils
from v440._utils.VList import VList


@keyalias(major=0, minor=1, micro=2, patch=2)
class Release(VList):
    def __add__(self, other, /) -> Self:
        other = type(self)(other)
        ans = self.copy()
        ans._data += other._data
        return ans

    @overloadable
    def __delitem__(self, key) -> bool:
        return type(key) is slice

    @__delitem__.overload(False)
    def __delitem__(self, key) -> None:
        key = operator.index(key)
        if key < len(self):
            del self._data[key]

    @__delitem__.overload(True)
    def __delitem__(self, key) -> None:
        key = utils.torange(key, len(self))
        key = [k for k in key if k < len(self)]
        key.sort(reverse=True)
        for k in key:
            del self._data[k]

    @overloadable
    def __getitem__(self, key) -> bool:
        return type(key) is slice

    @__getitem__.overload(False)
    def __getitem__(self, key) -> int:
        key = operator.index(key)
        return self._getitem_int(key)

    @__getitem__.overload(True)
    def __getitem__(self, key) -> list:
        key = utils.torange(key, len(self))
        ans = [self._getitem_int(i) for i in key]
        return ans

    @overloadable
    def __setitem__(self, key, value) -> bool:
        return type(key) is slice

    @__setitem__.overload(False)
    def __setitem__(self, key: SupportsIndex, value):
        key = operator.index(key)
        self._setitem_int(key, value)

    @__setitem__.overload(True)
    def __setitem__(self, key: SupportsIndex, value):
        key = utils.torange(key, len(self))
        self._setitem_range(key, value)

    def __str__(self) -> str:
        return self.format()

    def _getitem_int(self, key: int) -> int:
        if key < len(self):
            return self._data[key]
        else:
            return 0

    def _setitem_int(self, key: int, value):
        value = utils.numeral(value)
        length = len(self)
        if length > key:
            self._data[key] = value
            return
        if value == 0:
            return
        self._data.extend([0] * (key - length))
        self._data.append(value)

    @overloadable
    def _setitem_range(self, key: range, value: Any):
        return key.step == 1

    @_setitem_range.overload(False)
    def _setitem_range(self, key: range, value: Any):
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

    @_setitem_range.overload(True)
    def _setitem_range(self, key: range, value: Any):
        data = self.data
        ext = max(0, key.start - len(data))
        data += ext * [0]
        value = self._tolist(value, slicing="always")
        data = data[: key.start] + value + data[key.stop :]
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @staticmethod
    def _tolist(value, *, slicing) -> list:
        if value is None:
            return []
        if isinstance(value, int):
            return [utils.numeral(value)]
        if not isinstance(value, str):
            if hasattr(value, "__iter__"):
                return [utils.numeral(x) for x in value]
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

    def bump(self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        index = operator.index(index)
        amount = operator.index(amount)
        x = self._getitem_int(index) + amount
        self._setitem_int(index, x)
        if index != -1:
            self.data = self.data[: index + 1]

    @property
    def data(self) -> list:
        return list(self._data)

    @data.setter
    def data(self, value) -> None:
        value = self._tolist(value, slicing="always")
        while value and value[-1] == 0:
            value.pop()
        self._data = value

    def format(self, cutoff=None) -> str:
        format_spec = str(cutoff) if cutoff else ""
        i = int(format_spec) if format_spec else None
        ans = self[:i]
        if len(ans) == 0:
            ans += [0]
        ans = [str(x) for x in ans]
        ans = ".".join(ans)
        return ans
