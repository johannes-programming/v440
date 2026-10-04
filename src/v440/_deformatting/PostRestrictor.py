"""Restrict post-release segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["PostRestrictor"]
from typing import Self

from v440._deformatting.QualABCRestrictor import QualABCRestrictor


class PostRestrictor(QualABCRestrictor):
    """Track formatting constraints for a post-release qualifier."""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        if self.pair is None:
            return ""
        if self.pair.mag <= 1 and self.pair.mag and self.pair.lit == ".post":
            return ""
        if self.pair.mag <= 1 and self.pair.lit == "-":
            return "-"
        return self.pair.lit + self.pair.mag * "#"
