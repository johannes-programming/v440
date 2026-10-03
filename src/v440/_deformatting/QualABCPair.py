"""Pair a qualifier literal with a magnitude clue."""

from __future__ import annotations

__all__: list[str] = ["QualABCPair"]

import string
from typing import NamedTuple, Self


class QualABCPair(NamedTuple):
    """Store a qualifier literal together with its numeric-width constraint."""

    lit: str
    mag: int

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        return self.lit + self.mag * "#"

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        """Parse formatting constraints from one format-specification fragment."""
        lit: str
        lit = text.rstrip("#")
        return cls(lit=lit, mag=len(text) - len(lit))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        """Infer formatting constraints from one observed rendering."""
        lit: str
        mag: str
        lit = text.rstrip(string.digits)
        mag = text[len(lit) :]
        if mag.startswith("0"):
            return cls(lit=lit, mag=len(mag))
        else:
            return cls(lit=lit, mag=-len(mag))

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        if self.lit != other.lit:
            raise ArithmeticError
        if self.mag == other.mag:
            return self
        if self.mag + other.mag <= 0:
            return max(self, other)
        raise ArithmeticError
