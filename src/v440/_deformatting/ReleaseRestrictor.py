"""Provide the Release class for version release tuples in v440."""

from __future__ import annotations

__all__: list[str] = ["ReleaseRestrictor"]

import operator
from typing import Self, SupportsIndex

from v440._deformatting.Mag import Mag


class ReleaseRestrictor(tuple[Mag, ...]):
    """Track formatting constraints for numeric release components."""

    def best(self: Self, /) -> str:
        """Return the shortest release format fragment satisfying these width constraints."""
        ans: str
        ans = ".".join("#" * mag for mag in self).rstrip(".")
        return ans

    @classmethod
    def by_string(cls: type[Self], string: str, /) -> Self:
        """Infer release-component width constraints from one observed rendering."""
        mags: list[Mag]
        part: str
        mags = list()
        for part in string.split("."):
            if part == "0" or not part.startswith("0"):
                mags.append(Mag(-len(part)))
            else:
                mags.append(Mag(len(part)))
        if string.endswith(".0"):
            mags[-1] = Mag(1)
        return cls(tuple(mags))

    def union(self: Self, other: Self, /) -> Self:
        """Combine these release-width constraints with another compatible observation."""
        left_magnitude: Mag
        mags: list[Mag]
        right_magnitude: Mag
        mags = list()
        for left_magnitude, right_magnitude in zip(self, other):
            mags.append(left_magnitude.union(right_magnitude))
        for left_magnitude in self[len(mags) :] or other[len(mags) :]:
            Mag(0).union(left_magnitude)
        return type(self)(tuple(mags))


def item_parse(value: SupportsIndex, /) -> int:
    """Convert one release-format width to a nonnegative integer."""
    ans: int
    ans = operator.index(value)
    if ans < 0:
        raise ValueError
    return ans
