from __future__ import annotations

import itertools
import operator
import string as string_
from typing import *

import setdoc

from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.ListStringer import ListStringer

__all__ = ["Local"]


class Local(ListStringer):
    __slots__ = ()

    string: str
    packaging: Optional[str]
    data: tuple

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._data = ()
        self.string = string

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        return tuple(map(cls._item_parse, value))

    @classmethod
    def _deformat(cls: type, info: dict[str, Self]) -> str:
        m: int = max(*map(len, info.values()))
        s: str
        t: str
        i: int
        parts: list = list(map(set, [""] * m))
        for s in info.keys():
            for i, t in enumerate(Cfg.cfg.patterns["local_splitter"].split(s)):
                parts[i].add(t)
        for i in range(0, m, 2):
            if i % 2:
                (parts[i],) = parts[i]
            else:
                parts[i] = cls._deformat_part(parts[i])
        s = "".join(parts)
        return s

    @classmethod
    def _deformat_part(cls: type, part: set[str]) -> str:
        s: str
        data: set[int] = set(
            len(s) for s in part if s.startswith("0") and not s.strip(string_.digits)
        )
        f: int
        if len(data):
            (f,) = data
            if f > min(*map(len, part)):
                raise ValueError
        else:
            f = 0
        i: int
        n: int
        cases: list = ["#"] * max(0, *map(len, part))
        for i, s in itertools.chain(*map(enumerate, part)):
            if s in string_.digits:
                continue
            if s in string_.ascii_uppercase:
                n = "^"
            else:
                n = "~"
            if "#" == cases[i]:
                cases[i] = n
            elif n != cases[i]:
                raise ValueError
        s += "".join(cases).replace("#", "~").rstrip("~")
        s = "#" * f + s
        return s

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        if spec.strip("#^~.-_"):
            raise ValueError
        return dict(spec=spec)

    def _format_parsed(self: Self, *, spec: str) -> str:
        ans: str = ""
        data: list = list(self.data)
        tail: str = spec
        part: str
        while len(data):
            part, tail = self._format_item(data.pop(0), tail)
            ans += part
        ans = ans[:-1]
        return ans

    @classmethod
    def _format_item(cls: type, item: int | str, spec: str) -> tuple[str, str]:
        sharps: str
        mask: str
        sep: str
        right: str = spec
        sharps, right = cls._format_l(right, "#")
        mask, right = cls._format_l(right, "^~")
        if right:
            sep = right[0]
            right = right[1:]
        else:
            sep = "."
        part: str
        if isinstance(item, int):
            part = format(item, "0%sd" % len(sharps))
        else:
            part = cls._format_mask(item, mask)
        return part + sep, right

    @classmethod
    def _format_l(cls: type, value: str, chars: str) -> tuple:
        i: int = 0
        while i < len(value):
            if value[i] in chars:
                i += 1
            else:
                break
        return value[:i], value[i:]

    @classmethod
    def _format_mask(cls: type, item: str, mask: str):
        ans: list = list(item)
        i: int = 0
        while i < len(ans) and i < len(mask):
            if mask[i] == "^":
                ans[i] = ans[i].upper()
            i += 1
        return "".join(ans)

    @classmethod
    def _item_parse(cls: type, value: Any) -> int | str:
        ans: int | str
        try:
            ans = operator.index(value)
        except Exception:
            ans = str(value).lower()
            if ans.strip(string_.digits + string_.ascii_lowercase):
                raise
            if not ans.strip(string_.digits):
                ans = int(ans)
        else:
            if ans < 0:
                raise ValueError
        return ans

    @classmethod
    def _sort(cls: type, value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self.data = ()
            return
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    @property
    def packaging(self: Self) -> Optional[str]:
        if self:
            return str(self)
        else:
            return

    @packaging.setter
    @guard
    def packaging(self: Self, value: Any) -> None:
        if value is None:
            self.string = ""
        else:
            self.string = value
