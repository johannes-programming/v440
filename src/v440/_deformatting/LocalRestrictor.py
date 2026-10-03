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
    """Track case and numeric-shape constraints for one local literal."""

    data: str = ""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        return self.data.replace("#", "~").rstrip("~")

    @classmethod
    def by_item(cls: type[Self], item: str, /) -> Self:
        """Infer formatting constraints from one observed item."""
        data: str
        character: str
        data = "".join(
            (
                "#"
                if character in string_.digits
                else "^" if character in string_.ascii_uppercase else "~"
            )
            for character in item
        ).rstrip("#")
        return cls(data)

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        merged: list[str]
        left: str
        right: str
        merged = []
        for left, right in zip(self.data, other.data):
            if left == "#":
                merged.append(right)
            elif right == "#" or left == right:
                merged.append(left)
            else:
                raise ValueError
        merged.extend(self.data[len(merged) :] or other.data[len(merged) :])
        return type(self)("".join(merged))


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

    evens: tuple[EvenAccumulation, ...]
    odds: tuple[str, ...]

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        result: str
        accumulation: EvenAccumulation
        separator: str
        result = ""
        for accumulation, separator in zip(self.evens, self.odds):
            result += accumulation.best()
            result += separator
        if len(self.odds) < len(self.evens):
            result += self.evens[-1].best()
        result = result.rstrip(".")
        return result

    @classmethod
    def by_parts(cls: type[Self], /, *parts: str) -> Self:
        """Infer formatting constraints from alternating observed parts."""
        return cls(
            evens=tuple(map(EvenAccumulation.by_item, parts[::2])),
            odds=parts[1::2],
        )

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        accumulations: tuple[EvenAccumulation, ...]
        accumulations = tuple(map(EvenAccumulation.union, self.evens, other.evens))
        accumulations += (
            self.evens[len(accumulations) :]
            or other.evens[len(accumulations) :]
        )
        if any(map(operator.ne, self.odds, other.odds)):
            raise ValueError
        return type(self)(
            evens=accumulations,
            odds=max(self.odds, other.odds, key=len),
        )
