from __future__ import annotations

import string as string_
from typing import *

from v440._utils import forms
from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.QualSpec import QualSpec
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

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        ans: str = ""
        strings: set
        for x in ("a", "b", "rc"):
            strings = {s for s, o in info.items() if o.lit == x}
            ans += forms.qualdeform(*strings, hollow=x)
        return ans

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        m: dict = Cfg.fullmatches("pre_f", spec)
        ans: dict = dict()
        ans["a"] = QualSpec.by_spec(m["a_f"])
        ans["b"] = QualSpec.by_spec(m["b_f"])
        ans["rc"] = QualSpec.by_spec(m["rc_f"])
        return ans

    def _format_parsed(self: Self, *, a: QualSpec, b: QualSpec, rc: QualSpec) -> str:
        spec: QualSpec
        if self.lit == "a":
            spec = a
        elif self.lit == "b":
            spec = b
        elif self.lit == "rc":
            spec = rc
        else:
            return ""
        if spec.head == "":
            return self.lit + str(self.num)
        if self.num or spec.mag:
            return spec.head + format(self.num, f"0{spec.mag}d")
        if spec.head[-1] in ".-_":
            return spec.head[:-1]
        return spec.head

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
