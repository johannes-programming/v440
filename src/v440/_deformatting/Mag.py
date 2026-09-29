from __future__ import annotations

__all__: list[str] = ["Mag"]


from typing import Self

from .MagJoker import MagJoker


class Mag(int):
    def best(self: Self, /) -> str:
        return "#" * self

    def intersection(self: Self, other: Self | MagJoker, /) -> Self:
        if isinstance(other, MagJoker) or self == other:
            return self
        if self + other <= 0:
            return max(self, other)
        raise ArithmeticError
