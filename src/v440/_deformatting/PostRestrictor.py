__all__: list[str] = ["PostRestrictor"]
from typing import Self

from .QualABCRestrictor import QualABCRestrictor


class PostRestrictor(QualABCRestrictor):
    def best(self: Self, /) -> str:
        if self.pair is None:
            return ""
        if self.pair.mag <= 1 and self.pair.mag and self.pair.lit == ".post":
            return ""
        if self.pair.mag <= 1 and self.pair.lit == "-":
            return "-"
        return self.pair.lit + self.pair.mag * "#"
