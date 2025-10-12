from __future__ import annotations

import operator
from typing import *

from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer

__all__ = ["Dev"]


class Dev(QualStringer):

    __slots__ = ()
    string: str
    packaging: str
    lit: str
    num: int

    def _cmp(self: Self) -> tuple:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    def _format(self: Self, spec: str, /) -> str:
        x: str
        n: int
        if spec:
            x = spec.rstrip("0")
            n = len(spec) - len(x)
        else:
            x = ".dev"
            n = 1
        t: str = x.lower().replace("_", ".").replace("-", ".")
        if t not in ("dev", ".dev", "dev.", ".dev."):
            raise ValueError
        if t.endswith("."):
            n = 1
        ans: str
        if self.lit == "":
            ans = ""
        elif self.num or n:
            ans = x + format(self.num, "0%sd" % n)
        else:
            ans = x
        return ans

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self) -> Optional[int]:
        if self:
            return self.num
        else:
            return

    @packaging.setter
    @guard
    def packaging(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
