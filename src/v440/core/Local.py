"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Local"]

import operator
import string as string_
from dataclasses import dataclass
from typing import Any, NamedTuple, Self

from iterflat import iterflat

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.ListABC import ListABC


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
    s = "".join(cases).replace("#", "~").rstrip("~")
    return s


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


def item_parse(value: Any, /) -> int | str:
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


class LocalAccumulation(NamedTuple):
    evens: tuple[frozenset[str], ...]
    odds: tuple[frozenset[str], ...]

    def best(self: Self, /, *, forbids_empty: bool = False) -> str:
        i: int
        part: frozenset[str]
        parts: list[str]
        ans: str
        s: str
        parts = []
        for i, part in enumerate(self.parts):
            if i % 2:
                (s,) = part
            else:
                s = deformat_part(set(part))
            parts.append(s)
        ans = "".join(parts).rstrip(".")
        if forbids_empty and not ans:
            return "#"
        return ans

    @classmethod
    def by_parts(cls: type[Self], /, *parts: str) -> Self:
        parts_: tuple[frozenset[str], ...]
        parts_ = tuple(frozenset({x}) for x in parts)
        return cls(
            evens=parts_[::2],
            odds=parts_[1::2],
        )

    def intersection(self: Self, other: Self, /) -> Self:
        part: frozenset[str]
        evens: list[frozenset[str]]
        odds: list[frozenset[str]]
        evens = list(map(operator.or_, self.evens, other.evens))
        evens += self.evens[len(evens) :] or other.evens[len(evens) :]
        for part in evens:
            deformat_part(set(part))
        odds = list(map(operator.or_, self.odds, other.odds))
        odds += self.odds[len(odds) :] or other.odds[len(odds) :]
        for part in odds:
            if len(part) > 1:
                raise ValueError
        return type(self)(evens=tuple(evens), odds=tuple(odds))

    @property
    def parts(self: Self, /) -> tuple[frozenset[str], ...]:
        ans: list[frozenset[str]]
        ans = list()
        while True:
            try:
                ans.append(self[len(ans) % 2][len(ans) // 2])
            except IndexError:
                break
        return tuple(ans)


class Local(ListABC[int | str]):
    __slots__ = ()

    @classmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> tuple[int | str, ...]:
        return tuple(map(item_parse, value))

    def _deformat(self: Self, body: str, /) -> LocalAccumulation:
        if self:
            return LocalAccumulation.by_parts(
                *Cfg.cfg.patterns["local_splitter"].split(body)
            )
        else:
            return LocalAccumulation.by_parts()

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
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
        return tuple(split)

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
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
    def _sort(cls: type[Self], value: Any, /) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str, /) -> None:
        v: str
        if value == "":
            self.data = ()
            return
        v = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    @property
    def packaging(self: Self, /) -> str | None:
        if self:
            return str(self)
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: Any, /) -> None:
        if value is None:
            self.string = ""
        else:
            self.string = value

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        self.data = sorted(
            self,
            key=sort_key if key is None else key,
            reverse=reverse,
        )


def sort_key(item: int | str, /) -> tuple[bool, int | str]:
    "Return key for sorting int before str in Local."
    return isinstance(item, int), item
