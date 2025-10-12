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
        if spec:
            raise ValueError
        if self.lit:
            return self.lit + str(self.num)
        else:
            return ""

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
