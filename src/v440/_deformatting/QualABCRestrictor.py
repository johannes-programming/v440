"""Restrict one qualifier segment while deformatting."""

from __future__ import annotations

__all__: list[str] = ["QualABCRestrictor"]

from dataclasses import dataclass
from typing import Self

from v440._deformatting.QualABCPair import QualABCPair


@dataclass(frozen=True)
class QualABCRestrictor:
    """Represent QualABCRestrictor."""

    pair: QualABCPair | None = None

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        if self.pair is None:
            return ""
        else:
            return self.pair.best()

    @classmethod
    def by_fields(cls: type[Self], /, lit: str, mag: int) -> Self:
        """Build an instance by fields."""
        return cls(QualABCPair(lit, mag))

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        """Build an instance by spec."""
        if text == "":
            return cls()
        else:
            return cls(QualABCPair.by_spec(text))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        """Build an instance by string."""
        if text == "":
            return cls()
        else:
            return cls(QualABCPair.by_string(text))

    def union(self: Self, other: Self, /) -> Self:
        """Unite this state with another."""
        if self.pair is None:
            return other
        if other.pair is None:
            return self
        return type(self)(self.pair.union(other.pair))
