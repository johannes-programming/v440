"""Restrict developmental segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["DevRestrictor"]
from typing import Self

from v440._deformatting.QualABCRestrictor import QualABCRestrictor


class DevRestrictor(QualABCRestrictor):
    """Track formatting constraints for a development qualifier."""

    def best(self: Self, /) -> str:
        """Return the shortest format fragment satisfying these constraints."""
        if self.pair is None:
            return ""
        if self.pair.lit == ".dev" and self.pair.mag and self.pair.mag <= 1:
            return ""
        return self.pair.lit + self.pair.mag * "#"
