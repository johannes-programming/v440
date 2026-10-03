"""Provide the Public class for public version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["PublicRestrictor"]


from dataclasses import dataclass
from typing import Self

from v440._deformatting.BaseRestrictor import BaseRestrictor
from v440._deformatting.QualRestrictor import QualRestrictor


@dataclass(frozen=True, kw_only=True)
class PublicRestrictor:
    """Represent PublicRestrictor."""
    base: BaseRestrictor
    qual: QualRestrictor

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        ans: str
        ans = self.base.best()
        ans += self.qual.best()
        return ans

    def union(self: Self, other: Self, /) -> Self:
        """Unite this state with another."""
        return type(self)(
            base=self.base.union(other.base),
            qual=self.qual.union(other.qual),
        )
