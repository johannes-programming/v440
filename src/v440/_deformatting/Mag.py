"""Represent a numeric magnitude used while deformatting."""

from __future__ import annotations

__all__: list[str] = ["Mag"]


from typing import Self

from .MagJoker import MagJoker


class Mag(int):
    """Represent Mag."""

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        return "#" * self

    def union(self: Self, other: Self | MagJoker, /) -> Self:
        """Unite this state with another."""
        if isinstance(other, MagJoker) or self == other:
            return self
        if self + other <= 0:
            return max(self, other)
        raise ArithmeticError
