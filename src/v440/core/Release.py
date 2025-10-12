from __future__ import annotations

import operator
import string as string_
from typing import *

import keyalias
import setdoc

from v440._utils.ListStringer import ListStringer
from v440._utils.releaseparse import deleting, getting, setting

__all__ = ["Release"]


@keyalias.getdecorator(major=0, minor=1, micro=2, patch=2)
class Release(ListStringer):
    __slots__ = ()

    string: str
    packaging: tuple
    data: tuple
    major: int
    minor: int
    micro: int
    patch: int

    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> None:
        self._data = deleting.delitem(self.data, key)

    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> int | list:
        return getting.getitem(self.data, key)

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._data = ()
        self.string = string

    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> None:
        self._data = setting.setitem(self.data, key, value)

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        v: list = list(map(cls._item_parse, value))
        while v and v[-1] == 0:
            v.pop()
        return v

    def _format(self: Self, format_spec: str) -> str:
        if format_spec.strip("0."):
            raise ValueError
        specs: list = format_spec.split(".")
        specs = list(map(len, specs))
        data: list = list(self.data)
        data += [0] * max(0, len(specs) - len(data))
        i: int = 0
        while i < len(data):
            if i < len(specs):
                data[i] = format(data[i], "0%sd" % specs[i])
            else:
                data[i] = str(data[i])
            i += 1
        return ".".join(data)

    @classmethod
    def _item_parse(cls: type, value: SupportsIndex) -> int:
        ans: int = operator.index(value)
        if ans < 0:
            raise ValueError
        return ans

    @classmethod
    def _sort(cls: type, value: int) -> int:
        return value

    def _string_fset(self: Self, value: str) -> None:
        if value.strip(string_.digits + "."):
            raise ValueError
        self.data = map(int, value.split("."))

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        x: int = getting.getitem_int(self.data, i) + a
        self._data = setting.setitem_int(self.data, i, x)
        if i != -1:
            self.data = self.data[: i + 1]

    packaging = ListStringer.data
