from __future__ import annotations

import operator
from typing import *

import setdoc
from keyalias import keyalias

from v440._utils.ListStringer import ListStringer

__all__ = ["Release"]


@keyalias(major=0, minor=1, micro=2, patch=2)
class Release(ListStringer):
    __slots__ = ()

    string: str
    data: tuple
    major: int
    minor: int
    micro: int
    patch: int

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._data = ()
        self.string = string

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        v: list = list(map(cls._item_parse, value))
        while v and v[-1] == 0:
            v.pop()
        return v

    def _format(self: Self, format_spec: str) -> str:
        data: list = list(self.data)
        i: int = self._format_r(format_spec)
        i = max(max(i, 1) - len(data), 0)
        data += [0] * i
        ans: str = ".".join(map(str, data))
        return ans

    @classmethod
    def _format_r(cls: type, format_spec: str) -> int:
        if format_spec == "":
            return 0
        if not format_spec.startswith("0"):
            raise ValueError
        if not format_spec.endswith("r"):
            raise ValueError
        if set(format_spec[:-1]) <= set("0123456789"):
            return int(format_spec[:-1])
        raise ValueError

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
        if value == "":
            self.data = ()
            return
        if value.strip("0123456789_-."):
            raise ValueError
        v: str = value
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = map(int, v.split("."))

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        d: list = list(self.data)
        if 0 <= i:
            d += [0] * max(0, i + 1 - len(d))
        d[i] += a
        self.data = d
