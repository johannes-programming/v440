"""Provide the Public class for public version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["PublicRestrictor"]


from dataclasses import dataclass
from typing import Self

from v440._deformatting.BaseRestrictor import BaseRestrictor
from v440._deformatting.QualRestrictor import QualRestrictor


@dataclass(frozen=True, kw_only=True)
class PublicRestrictor:
    """Track formatting constraints for a public version."""

    base: BaseRestrictor
    qual: QualRestrictor

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        result: str
        result = self.base.best()
        result += self.qual.best()
        return result

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        return type(self)(
            base=self.base.union(other.base),
            qual=self.qual.union(other.qual),
        )
