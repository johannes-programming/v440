"""Provide the Release class for version release tuples in v440."""

from __future__ import annotations

__all__: list[str] = ["ReleaseRestrictor"]

import operator
from typing import Self, SupportsIndex

from .._deformatting.Mag import Mag


class ReleaseRestrictor(tuple[Mag, ...]):

    def best(self: Self, /) -> str:
        ans: str
        ans = ".".join("#" * mag for mag in self).rstrip(".")
        return ans

    @classmethod
    def by_string(cls: type[Self], body: str, /) -> Self:
        mags: list[Mag]
        mags = list()
        for part in body.split("."):
            if part == "0" or not part.startswith("0"):
                mags.append(Mag(-len(part)))
            else:
                mags.append(Mag(len(part)))
        if body.endswith(".0"):
            mags[-1] = Mag(1)
        return cls(tuple(mags))

    def union(self: Self, other: Self, /) -> Self:
        mags: list[Mag]
        mags = list()
        for x, y in zip(self, other):
            mags.append(x.union(y))
        for x in self[len(mags) :] or other[len(mags) :]:
            Mag(0).union(x)
        return type(self)(tuple(mags))


def item_parse(value: SupportsIndex, /) -> int:
    ans: int
    ans = operator.index(value)
    if ans < 0:
        raise ValueError
    return ans
