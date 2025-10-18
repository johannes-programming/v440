from __future__ import annotations

from typing import *

from v440._utils import forms
from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer

__all__ = ["Pre"]


class Pre(QualStringer):

    __slots__ = ()
    string: str
    packaging: Optional[tuple[str, int]]
    lit: str
    num: int

    def _cmp(self: Self) -> tuple:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    def _format(self: Self, spec: str, /) -> str:
        matches: dict = Cfg.cfg.fullmatches("pre_f", spec)
        if not self:
            return ""
        match: Optional[str] = matches[f"pre_{self.lit}_f"]
        ans: str
        if match is None:
            ans = self.lit + str(self.num)
        else:
            ans = forms.qualform(match, self.num)
        return ans

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        return Cfg.cfg.data["phases"][value]

    @property
    def packaging(self: Self) -> Optional[tuple[str, int]]:
        if self:
            return self.lit, self.num
        else:
            return

    @packaging.setter
    @guard
    def packaging(self: Self, value: Optional[Iterable]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.num = 0
            self.lit, self.num = value
