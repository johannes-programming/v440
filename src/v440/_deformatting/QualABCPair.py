"""Pair a qualifier literal with a magnitude clue."""

from __future__ import annotations

__all__: list[str] = ["QualABCPair"]

import string as string_
from typing import NamedTuple, Self


class QualABCPair(NamedTuple):
    """Store a qualifier literal together with its numeric-width constraint."""

    lit: str
    mag: int

    def best(self: Self, /) -> str:
        """Return the shortest qualifier format fragment satisfying this literal and width."""
        return self.lit + self.mag * "#"

    @classmethod
    def by_spec(cls: type[Self], spec: str, /) -> Self:
        """Parse a qualifier format fragment into its literal and numeric width."""
        lit: str
        lit = spec.rstrip("#")
        return cls(lit=lit, mag=len(spec) - len(lit))

    @classmethod
    def by_string(cls: type[Self], string: str, /) -> Self:
        """Infer a qualifier literal and numeric-width constraint from one rendering."""
        lit: str
        mag: str
        lit = string.rstrip(string_.digits)
        mag = string[len(lit) :]
        if mag.startswith("0"):
            return cls(lit=lit, mag=len(mag))
        else:
            return cls(lit=lit, mag=-len(mag))

    def union(self: Self, other: Self, /) -> Self:
        """Combine two compatible literal and numeric-width constraints."""
        if self.lit != other.lit:
            raise ArithmeticError
        if self.mag == other.mag:
            return self
        if self.mag + other.mag <= 0:
            return max(self, other)
        raise ArithmeticError
