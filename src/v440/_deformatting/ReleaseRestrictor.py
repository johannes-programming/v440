"""Provide the Release class for version release tuples in v440."""

from __future__ import annotations

__all__: list[str] = ["ReleaseRestrictor"]

import operator
from typing import Self, SupportsIndex

from v440._deformatting.Mag import Mag


class ReleaseRestrictor(tuple[Mag, ...]):
    """Track formatting constraints for release-number components."""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        result: str
        result = ".".join("#" * mag for mag in self).rstrip(".")
        return result

    @classmethod
    def by_string(cls: type[Self], body: str, /) -> Self:
        """Infer formatting constraints from one observed rendering."""
        component: str
        magnitudes: list[Mag]
        magnitudes = list()
        for component in body.split("."):
            if component == "0" or not component.startswith("0"):
                magnitudes.append(Mag(-len(component)))
            else:
                magnitudes.append(Mag(len(component)))
        # A final literal .0 must remain distinguishable from an omitted trailing
        # zero, so retain a positive width constraint for that last component.
        if body.endswith(".0"):
            magnitudes[-1] = Mag(1)
        return cls(tuple(magnitudes))

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        component: str
        left_magnitude: Mag
        magnitudes: list[Mag]
        right_magnitude: Mag
        magnitudes = list()
        for left_magnitude, right_magnitude in zip(self, other):
            magnitudes.append(left_magnitude.union(right_magnitude))
        for left_magnitude in self[len(magnitudes) :] or other[len(magnitudes) :]:
            Mag(0).union(left_magnitude)
        return type(self)(tuple(magnitudes))


def item_parse(value: SupportsIndex, /) -> int:
    """Convert one release value to a nonnegative integer."""
    component: int
    component = operator.index(value)
    if component < 0:
        raise ValueError
    return component
