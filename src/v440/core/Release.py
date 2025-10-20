from __future__ import annotations

import operator
import string as string_
from typing import *

import keyalias
import setdoc
from iterprod import iterprod

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

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        m: int = 0
        s: str
        for s in info.keys():
            m = max(m, 1 + s.count("."))
        i: int
        t: str
        table: list[set] = list(map(set, [""] * m))
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(s.split(".")):
                table[i].add(t)
        ans: str = ".".join(map(cls._deformat_parts, table))
        while ans.endswith(".0"):
            ans = ans[:-2]
        ans = ans.replace("0", "")
        return ans

    @classmethod
    def _deformat_parts(cls: type, parts: set[str]) -> str:
        f: int = -1
        x: str
        for x in parts:
            if not x.startswith("0"):
                continue
            if f == -1:
                f = len(x)
                continue
            if f != len(x):
                raise ValueError
        if len(parts) and f > min(map(len, parts)):
            raise ValueError
        if f == -1:
            return "0"
        if f == 1:
            return ""
        return "#" * f

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> str:
        if spec.strip("#."):
            raise ValueError
        return dict(specs=tuple(map(cls._format_parse_spec, spec.split("."))))

    @classmethod
    def _format_parse_spec(cls: type, value: str) -> str:
        return f"0{len(value)}d"

    def _format_parsed(self: Self, *, specs: tuple) -> str:
        data: list = list(self)
        data += [0] * max(0, 0, len(specs) - len(self))
        parts: list = list(specs)
        parts += [""] * max(0, 0, len(self) - len(specs))
        ans: str = ".".join(map(format, data, parts))
        return ans

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
