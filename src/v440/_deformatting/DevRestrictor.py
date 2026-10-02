__all__: list[str] = ["DevRestrictor"]
from typing import Self

from .QualABCRestrictor import QualABCRestrictor


class DevRestrictor(QualABCRestrictor):
    def best(self: Self, /) -> str:
        if self.pair is None:
            return ""
        if self.pair.lit == ".dev" and self.pair.num and self.pair.num <= 1:
            return ""
        return self.pair.lit + self.pair.num * "#"
