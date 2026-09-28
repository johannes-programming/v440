__all__: list[str] = ["Mag"]


from typing import Self


class Mag(int):
    def intersection(self: Self, other: Self, /) -> Self:
        if self == other:
            return self
        if self + other <= 0:
            return max(self, other)
        raise ArithmeticError
