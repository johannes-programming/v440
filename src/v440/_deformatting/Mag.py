"""Represent a numeric magnitude used while deformatting."""

from __future__ import annotations

__all__: list[str] = ["Mag"]


from typing import Self

from v440._deformatting.MagJoker import MagJoker


class Mag(int):
    """Represent a constrained numeric field width while deformatting."""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        return "#" * self

    def union(self: Self, other: Self | MagJoker, /) -> Self:
        """Combine these constraints with another compatible observation."""
        if isinstance(other, MagJoker) or self == other:
            return self
        if self + other <= 0:
            return max(self, other)
        raise ArithmeticError
