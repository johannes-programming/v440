"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Local"]

import operator
import string as string_
from dataclasses import dataclass
from typing import Any, Self

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


@dataclass(frozen=True, kw_only=True)
class LocalDeformat:
    parts: tuple[frozenset[str], ...]

    def __and__(self: Self, other: Self, /) -> Self:
        i: int
        part: frozenset[str]
        parts: list[frozenset[str]]
        parts = []
        for i in range(max(len(self.parts), len(other.parts))):
            part = (self.parts[i] if i < len(self.parts) else frozenset()) | (
                other.parts[i] if i < len(other.parts) else frozenset()
            )
            if i % 2:
                if len(part) > 1:
                    raise ValueError
            else:
                deformat_part(set(part))
            parts.append(part)
        return type(self)(
            parts=tuple(parts),
        )

    def best(self: Self, /) -> str:
        i: int
        part: frozenset[str]
        parts: list[str]
        s: str
        parts = []
        for i, part in enumerate(self.parts):
            if i % 2:
                (s,) = part
            else:
                s = deformat_part(set(part))
            parts.append(s)
        return "".join(parts).rstrip(".")


class Local(ListABC[int | str]):
    __slots__ = ()

    @classmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> tuple[int | str, ...]:
        return tuple(map(item_parse, value))

    def _deformat(self: Self, body: str, /) -> LocalDeformat:
        return LocalDeformat(
            parts=(
                tuple(
                    frozenset({part})
                    for part in Cfg.cfg.patterns["local_splitter"].split(body)
                )
                if self
                else ()
            ),
        )

    @staticmethod
    def _deformat_origin() -> LocalDeformat:
        return LocalDeformat(
            parts=(),
        )

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
