"""Restrict developmental segments while deformatting versions."""

__all__: list[str] = ["DevRestrictor"]
from typing import Self

from .QualABCRestrictor import QualABCRestrictor


class DevRestrictor(QualABCRestrictor):
    """Represent DevRestrictor."""

    def best(self: Self, /) -> str:
        """Return the best of this state."""
        if self.pair is None:
            return ""
        if self.pair.lit == ".dev" and self.pair.mag and self.pair.mag <= 1:
            return ""
        return self.pair.lit + self.pair.mag * "#"
