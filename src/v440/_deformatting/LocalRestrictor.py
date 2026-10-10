"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["LocalRestrictor"]

import operator
import string as string_
from dataclasses import dataclass
from typing import NamedTuple, Self

from v440._deformatting.Mag import Mag
from v440._deformatting.MagJoker import MagJoker
from v440._utils.Cfg import Cfg


@dataclass(frozen=True)
class LitAccumulation:
    """Track case and numeric-shape constraints for one local literal."""

    data: str = ""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        return self.data.replace("#", "~").rstrip("~")

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        """Infer formatting constraints from one observed item."""
        return cls(item.translate(Cfg.cfg.local_trans).rstrip("#"))

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        ans: list[str]
        left_symbol: str
        right_symbol: str
        ans = []
        for left_symbol, right_symbol in zip(self.data, other.data):
            if left_symbol == "#":
                ans.append(right_symbol)
            elif right_symbol == "#" or left_symbol == right_symbol:
                ans.append(left_symbol)
            else:
                raise ValueError
        ans.extend(self.data[len(ans) :] or other.data[len(ans) :])
        return type(self)("".join(ans))


@dataclass(frozen=True, kw_only=True)
class EvenAccumulation:
    """Track formatting constraints for one local-version segment."""

    num: Mag | MagJoker = MagJoker.JOKER
    lit: LitAccumulation = LitAccumulation()

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
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
        """Combine these constraints with another compatible observation."""
        return type(self)(
            lit=self.lit.union(other.lit),
            num=self.num.union(other.num),
        )


class LocalRestrictor(NamedTuple):
    """Track formatting constraints for a local-version identifier."""

    segments: tuple[EvenAccumulation, ...]
    separators: tuple[str, ...]

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        ans: str
        segment: EvenAccumulation
        separator: str
        ans = ""
        for segment, separator in zip(self.segments, self.separators):
            ans += segment.best()
            ans += separator
        if len(self.separators) < len(self.segments):
            ans += self.segments[-1].best()
        ans = ans.rstrip(".")
        return ans

    @classmethod
    def by_parts(cls: type[Self], /, *parts: str) -> Self:
        """Infer formatting constraints from alternating observed parts."""
        return cls(
            segments=tuple(map(EvenAccumulation.by_item, parts[::2])),
            separators=parts[1::2],
        )

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        segments: tuple[EvenAccumulation, ...]
        segments = tuple(
            map(EvenAccumulation.union, self.segments, other.segments)
        )
        segments += (
            self.segments[len(segments) :] or other.segments[len(segments) :]
        )
        if any(map(operator.ne, self.separators, other.separators)):
            raise ValueError
        return type(self)(
            segments=segments,
            separators=max(self.separators, other.separators, key=len),
        )
