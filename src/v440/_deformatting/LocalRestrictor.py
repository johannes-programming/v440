"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["LocalRestrictor"]

import operator
import string as string_
from dataclasses import dataclass
from typing import NamedTuple, Self

from v440._deformatting.Mag import Mag
from v440._deformatting.MagJoker import MagJoker


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

    def union(self: Self, other: Self, /) -> Self:
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


@dataclass(frozen=True, kw_only=True)
class EvenAccumulation:
    num: Mag | MagJoker = MagJoker.JOKER
    lit: LitAccumulation = LitAccumulation()

    def best(self: Self, /) -> str:
        return self.num.best() + self.lit.best()

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        if item.strip(string_.digits):
            return cls(lit=LitAccumulation.by_item(item))
        if len(item) == 1:
            return cls(num=Mag())
        if item.startswith("0"):
            return cls(num=Mag(len(item)))
        return cls(num=Mag(-len(item)))

    def union(self: Self, other: Self, /) -> Self:
        return type(self)(
            lit=self.lit.union(other.lit),
            num=self.num.union(other.num),
        )


class LocalRestrictor(NamedTuple):
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
        ans = ans.rstrip(".")
        return ans

    @classmethod
    def by_parts(cls: type[Self], /, *parts: str) -> Self:
        return cls(
            evens=tuple(map(EvenAccumulation.by_item, parts[::2])),
            odds=parts[1::2],
        )

    def union(self: Self, other: Self, /) -> Self:
        evens: tuple[EvenAccumulation, ...]
        evens = tuple(map(EvenAccumulation.union, self.evens, other.evens))
        evens += self.evens[len(evens) :] or other.evens[len(evens) :]
        if any(map(operator.ne, self.odds, other.odds)):
            raise ValueError
        return type(self)(
            evens=evens,
            odds=max(self.odds, other.odds, key=len),
        )
