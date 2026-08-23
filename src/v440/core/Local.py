"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Local"]

import operator
import string as string_
from collections import abc
from typing import Any, Self

import setdoc
from iterflat import iterflat

from v440._utils.Cfg import Cfg
from v440.abc.ListABC import ListABC


class Local(ListABC[int | str]):
    __slots__ = ()

    @classmethod
    def _deformat(
        cls: type[Self],
        info: dict[str, Self],
        /,
    ) -> str:
        m: int
        s: str
        t: str
        i: int
        parts: list[Any]
        if 0 == len(info):
            return ""
        m = max(map(len, info.values()))
        if m == 0:
            return ""
        parts = list(map(set, [""] * (2 * m - 1)))
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(Cfg.cfg.patterns["local_splitter"].split(s)):
                parts[i].add(t)
        for i in range(len(parts)):
            if i % 2:
                (parts[i],) = parts[i]
            else:
                parts[i] = deformat_part(parts[i])
        s = "".join(parts).rstrip(".")
        return s

    @classmethod
    def _format_parse(
        cls: type[Self],
        spec: str,
        /,
    ) -> abc.Iterable[Any]:
        l: str
        m: int
        x: str
        y: str
        parts: list[Any]
        split: list[tuple[int, str, str]]
        if spec.strip("#^~.-_"):
            raise ValueError
        parts = Cfg.cfg.patterns["local_splitter"].split(spec) + ["."]
        split = []
        for x, y in zip(parts[::2], parts[1::2]):
            l = x.lstrip("#")
            if "#" in l:
                raise ValueError
            m = len(x) - len(l)
            if m == 1:
                m = 0
            l = l.rstrip("~")
            split.append((m, l, y))
        while len(split) and split[-1] == (0, "", "."):
            split.pop()
        return split

    def _format_parsed(
        self: Self,
        /,
        *parsed: Any,
    ) -> str:
        ans: str
        item: int | str
        index: int
        s: str
        t: str
        x: int
        y: str
        z: str
        ans = ""
        for index, item in enumerate(self):
            if index < len(parsed):
                x, y, z = parsed[index]
            else:
                x, y, z = 0, "", "."
            if isinstance(item, int):
                ans += format(item, f"0{x}d")
                ans += z
                continue
            for s, t in zip(y, item):
                ans += t.upper() if s == "^" else t
            ans += item[len(y) :]
            ans += z
        ans = ans[:-1]
        return ans

    @classmethod
    def _mutable_parse(
        cls: type[Self],
        other: list[Any],
        /,
    ) -> tuple[int | str, ...]:
        return tuple(map(parse_item, other))

    @classmethod
    def _sort(
        cls: type[Self],
        value: Any,
        /,
    ) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(
        self: Self,
        value: str,
        /,
    ) -> None:
        v: str
        if value == "":
            self[:] = ()
            return
        v = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self[:] = v.split(".")

    @property
    def packaging(self: Self, /) -> str | None:
        if self:
            return str(self)
        else:
            return None

    @packaging.setter
    def packaging(self: Self, value: Any, /) -> None:
        if value is None:
            self.string = ""
        else:
            self.string = value

    @setdoc.basic
    def sort(
        self: Self,
        /,
        *,
        key: Any = None,
        reverse: Any = False,
    ) -> None:
        mutable: list[int | str]
        with self.__mutate__() as mutable:
            mutable.sort(
                key=sort_key if key is None else key,
                reverse=reverse,
            )


def deformat_lits(part: set[str], /) -> str:
    i: int
    s: str
    t: str
    cases: list[str]
    cases = ["#"] * max(map(len, part), default=0)
    for i, s in iterflat(map(enumerate, part)):
        if s in string_.digits:
            continue
        if s in string_.ascii_uppercase:
            t = "^"
        else:
            t = "~"
        if "#" == cases[i]:
            cases[i] = t
            continue
        if t != cases[i]:
            raise ValueError
    return "".join(cases).replace("#", "~").rstrip("~")


def deformat_nums(part: set[str], /) -> int:
    n: int
    s: str
    n = 1
    for s in part:
        if s.startswith("0"):
            n = max(n, len(s))
    if n > min(map(len, part), default=1):
        raise ValueError
    elif n == 1:
        return 0
    else:
        return n


def deformat_part(part: set[str], /) -> str:
    lits: set[str]
    nums: set[str]
    s: str
    lits = set()
    nums = set()
    for s in part:
        if s.strip(string_.digits):
            lits.add(s)
        else:
            nums.add(s)
    s = "#" * deformat_nums(nums)
    s += deformat_lits(lits)
    return s


def parse_item(value: Any, /) -> int | str:
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


def sort_key(item: int | str, /) -> tuple[bool, int | str]:
    "Return key for sorting int before str in Local."
    return isinstance(item, int), item
