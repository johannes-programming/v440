"""Represent an unconstrained magnitude while deformatting."""

from __future__ import annotations

__all__: list[str] = ["MagJoker"]


import enum
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from v440._deformatting.Mag import Mag


class MagJoker(enum.Enum):
    """Represent an unconstrained numeric field width while deformatting."""

    JOKER = None

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        return ""

    def union(self: Self, other: Self | Mag, /) -> Self | Mag:
        """Combine these constraints with another compatible observation."""
        return other
