"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Local"]

import operator
import string as string_
from dataclasses import dataclass
from typing import Any, Final, NamedTuple, Self

from v440._deformatting.Mag import Mag
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.ListABC import ListABC


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


@dataclass(frozen=True)
class LitAccumulation:
    data: str = ""

    def best(self: Self, /) -> str:
        return self.data.replace("#", "~").rstrip("~")

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        data: str
        s: str
        data = "".join(
            (
                "#"
                if s in string_.digits
                else "^" if s in string_.ascii_uppercase else "~"
            )
            for s in item
        ).rstrip("#")
        return cls(data)

    def intersection(self: Self, other: Self, /) -> Self:
        ans: list[str]
        x: str
        y: str
        ans = []
        for x, y in zip(self.data, other.data):
            if x == "#":
                ans.append(y)
            elif y == "#" or x == y:
                ans.append(x)
            else:
                raise ValueError
        ans.extend(self.data[len(ans) :] or other.data[len(ans) :])
        return type(self)("".join(ans))


@dataclass(frozen=True)
class NumAccumulation:
    data: Mag | None = None

    def best(self: Self, /) -> str:
        if self.data is None:
            return ""
        else:
            return "#" * self.data

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        if len(item) == 1:
            return cls(data=Mag())
        if item.startswith("0"):
            return cls(data=Mag(len(item)))
        return cls(data=Mag(-len(item)))

    def intersection(self: Self, other: Self, /) -> Self:
        if self.data is None:
            return other
        if other.data is None:
            return self
        return type(self)(self.data.intersection(other.data))


@dataclass(frozen=True, kw_only=True)
class EvenAccumulation:
    lit: LitAccumulation = LitAccumulation()
    num: NumAccumulation = NumAccumulation()

    def best(self: Self, /) -> str:
        return self.num.best() + self.lit.best()

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        if item.strip(string_.digits):
            return cls(lit=LitAccumulation.by_item(item))
        else:
            return cls(num=NumAccumulation.by_item(item))

    def intersection(self: Self, other: Self, /) -> Self:
        return type(self)(
            lit=self.lit.intersection(other.lit),
            num=self.num.intersection(other.num),
        )


class LocalAccumulation(NamedTuple):
    evens: tuple[EvenAccumulation, ...]
    odds: tuple[str, ...]

    def best(self: Self, /) -> str:
        ans: str
        even: EvenAccumulation
        odd: str
        ans = ""
        for even, odd in zip(self.evens, self.odds):
            ans += even.best()
            ans += odd
        if len(self.odds) < len(self.evens):
            ans += self.evens[-1].best()
        return ans.rstrip(".")

    @classmethod
    def by_parts(cls: type[Self], /, *parts: str) -> Self:
        return cls(
            evens=tuple(map(EvenAccumulation.by_item, parts[::2])),
            odds=parts[1::2],
        )

    def intersection(self: Self, other: Self, /) -> Self:
        evens: tuple[EvenAccumulation, ...]
        evens = tuple(
            map(EvenAccumulation.intersection, self.evens, other.evens)
        )
        evens += self.evens[len(evens) :] or other.evens[len(evens) :]
        if any(map(operator.ne, self.odds, other.odds)):
            raise ValueError
        return type(self)(
            evens=evens,
            odds=max(self.odds, other.odds, key=len),
        )


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


def sort_key(item: int | str, /) -> tuple[bool, int | str]:
    "Return key for sorting int before str in Local."
    return isinstance(item, int), item
