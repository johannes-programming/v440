from __future__ import annotations

import operator
from typing import *

from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer

__all__ = ["Post"]


class Post(QualStringer):

    __slots__ = ()
    string: str
    packaging: Optional[int]
    lit: str
    num: int

    def _cmp(self: Self) -> int:
        if self.lit:
            return self.num
        else:
            return -1

    def _format(self: Self, spec: str, /) -> str:
        x: str
        n: int
        if spec:
            x = spec.rstrip("#")
            n = len(spec) - len(x)
        else:
            x = ".post"
            n = 1
        if self._format_test_lit(x) and not n:
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
    def _format_test_lit(cls: type, spec: str, /) -> bool:
        if spec == "-":
            return True
        t: str = spec.lower().replace("_", ".").replace("-", ".")
        if t.startswith("."):
            t = t[1:]
        ans: bool = t.endswith(".")
        if ans:
            t = t[:-1]
        if t in ("post", "r", "rev"):
            return ans
        raise ValueError

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        if value in ("-", "post", "r", "rev"):
            return "post"
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
            self.lit = "post"
            self.num = operator.index(value)
