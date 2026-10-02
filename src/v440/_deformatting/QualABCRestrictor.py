from __future__ import annotations

__all__: list[str] = ["QualABCRestrictor"]

import string
from dataclasses import dataclass
from typing import NamedTuple, Self


class QualABCPair(NamedTuple):
    lit: str
    num: int

    def best(self: Self, /) -> str:
        return self.lit + self.num * "#"

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        lit: str
        lit = text.rstrip("#")
        return cls(lit=lit, num=len(text) - len(lit))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        lit: str
        num: str
        lit = text.rstrip(string.digits)
        num = text[len(lit) :]
        if num.startswith("0"):
            return cls(lit=lit, num=len(num))
        else:
            return cls(lit=lit, num=-len(num))

    def union(self: Self, other: Self, /) -> Self:
        if self.lit != other.lit:
            raise ArithmeticError
        if self.num == other.num:
            return self
        if self.num + other.num <= 0:
            return max(self, other)
        raise ArithmeticError


@dataclass(frozen=True)
class QualABCRestrictor:
    pair: QualABCPair | None = None

    def best(self: Self, /) -> str:
        if self.pair is None:
            return ""
        else:
            return self.pair.best()

    @classmethod
    def by_spec(cls: type[Self], text: str, /) -> Self:
        if text == "":
            return cls()
        else:
            return cls(QualABCPair.by_spec(text))

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        if text == "":
            return cls()
        else:
            return cls(QualABCPair.by_string(text))

    def union(self: Self, other: Self, /) -> Self:
        if self.pair is None:
            return other
        if other.pair is None:
            return self
        return type(self)(self.pair.union(other.pair))
