from __future__ import annotations

import operator
from typing import *

from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer

__all__ = ["Dev"]


class Dev(QualStringer):

    __slots__ = ()
    string: str
    lit: str
    num: int

    def _cmp(self: Self) -> tuple:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    def _string_fset_minus(self: Self, value: str) -> None:
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
