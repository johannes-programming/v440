from __future__ import annotations

__all__: list[str] = ["MagJoker"]


import enum
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .Mag import Mag


class MagJoker(enum.Enum):
    JOKER = None

    def best(self: Self, /) -> str:
        return ""

    def union(self: Self, other: Self | Mag, /) -> Self | Mag:
        return other
