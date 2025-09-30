from __future__ import annotations

import operator
from typing import *

import setdoc
from keyalias import keyalias
from overloadable import Overloadable

from v440._utils import releaseparse
from v440._utils.ListStringer import ListStringer

__all__ = ["Release"]


@keyalias(major=0, minor=1, micro=2, patch=2)
class Release(ListStringer):
    __slots__ = ()

    string: str
    data: tuple[int]
    major: int
    minor: int
    micro: int
    patch: int

    @Overloadable
    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__delitem__.overload(False)
    @setdoc.basic
    def __delitem__(self: Self, key: SupportsIndex) -> None:
        i: int = operator.index(key)
        if i >= len(self):
            return
        data: list = list(self.data)
        del data[i]
        self.data = data

    @__delitem__.overload(True)
    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> None:
        r: range = releaseparse.torange(key, len(self))
        k: Any
        l: list = [k for k in r if k < len(self)]
        l.sort(reverse=True)
        data: list = list(self.data)
        for k in l:
            del data[k]
        self.data = data

    @Overloadable
    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__getitem__.overload(False)
    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> int:
        i: int = operator.index(key)
        ans: int = self._getitem_int(i)
        return ans

    @__getitem__.overload(True)
    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> list:
        r: range = releaseparse.torange(key, len(self))
        m: map = map(self._getitem_int, r)
        ans: list = list(m)
        return ans

    @Overloadable
    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> bool:
        return type(key) is slice

    @__setitem__.overload(False)
    @setdoc.basic
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        i: int = operator.index(key)
        self._setitem_int(i, value)

    @__setitem__.overload(True)
    @setdoc.basic
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        k: range = releaseparse.torange(key, len(self))
        self._setitem_range(k, value)

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        v: list = releaseparse.tolist(value, slicing="always")
        while v and v[-1] == 0:
            v.pop()
        return v

    def _format(self: Self, format_spec: str) -> str:
        i: Optional[int]
        if format_spec:
            i = int(format_spec)
        else:
            i = None
        l: list = self[:i]
        if len(l) == 0:
            l += [0]
        l = list(map(str, l))
        ans: str = ".".join(l)
        return ans

    def _getitem_int(self: Self, key: int) -> int:
        if key < len(self):
            return self.data[key]
        else:
            return 0

    def _setitem_int(self: Self, key: int, value: Any) -> Any:
        v: int = releaseparse.numeral(value)
        if key < len(self):
            data = list(self.data)
            data[key] = v
            self.data = data
            return
        if v == 0:
            return
        self._data += (0,) * (key - len(self))
        self._data += (v,)

    @Overloadable
    def _setitem_range(self: Self, key: range, value: Any) -> bool:
        return key.step == 1

    @_setitem_range.overload(False)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        key: list = list(key)
        value: list = releaseparse.tolist(value, slicing=len(key))
        if len(key) != len(value):
            e = "attempt to assign sequence of size %s to extended slice of size %s"
            e %= (len(value), len(key))
            raise ValueError(e)
        ext: int = max(0, max(*key) + 1 - len(self))
        data: list = list(self.data)
        data += [0] * ext
        for k, v in zip(key, value):
            data[k] = v
        self.data = data

    @_setitem_range.overload(True)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        data: list = list(self.data)
        ext: int = max(0, key.start - len(data))
        data += ext * [0]
        l: list = releaseparse.tolist(value, slicing="always")
        data = data[: key.start] + l + data[key.stop :]
        self.data = data

    @classmethod
    def _sort(cls: type, value: int) -> int:
        return value

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self.data = ()
            return
        v: str = value
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        x: int = self._getitem_int(i) + a
        self._setitem_int(i, x)
        if i != -1:
            self.data = self.data[: i + 1]
