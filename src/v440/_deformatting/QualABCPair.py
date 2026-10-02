from __future__ import annotations

__all__: list[str] = ["QualABCPair"]

import string
from typing import NamedTuple, Self


class QualABCPair(NamedTuple):
    lit: str
    mag: int

    def best(self: Self, /) -> str:
        return self.lit + self.mag * "#"

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        lit: str
        lit = text.rstrip("#")
        return cls(lit=lit, mag=len(text) - len(lit))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        lit: str
        mag: str
        lit = text.rstrip(string.digits)
        mag = text[len(lit) :]
        if mag.startswith("0"):
            return cls(lit=lit, mag=len(mag))
        else:
            return cls(lit=lit, mag=-len(mag))

    def union(self: Self, other: Self, /) -> Self:
        if self.lit != other.lit:
            raise ArithmeticError
        if self.mag == other.mag:
            return self
        if self.mag + other.mag <= 0:
            return max(self, other)
        raise ArithmeticError
