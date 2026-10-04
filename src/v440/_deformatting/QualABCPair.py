"""Pair a qualifier literal with a magnitude clue."""

from __future__ import annotations

__all__: list[str] = ["QualABCPair"]

import string
from typing import NamedTuple, Self


class QualABCPair(NamedTuple):
    """Represent QualABCPair."""

    lit: str
    mag: int

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        return self.lit + self.mag * "#"

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        """Build an instance by spec."""
        lit: str
        lit = text.rstrip("#")
        return cls(lit=lit, mag=len(text) - len(lit))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        """Build an instance by string."""
        lit: str
        mag: str
        lit = text.rstrip(string.digits)
        mag = text[len(lit) :]
        if mag.startswith("0"):
            return cls(lit=lit, mag=len(mag))
        else:
            return cls(lit=lit, mag=-len(mag))

    def union(self: Self, other: Self, /) -> Self:
        """Unite this state with another."""
        if self.lit != other.lit:
            raise ArithmeticError
        if self.mag == other.mag:
            return self
        if self.mag + other.mag <= 0:
            return max(self, other)
        raise ArithmeticError
