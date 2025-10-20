from __future__ import annotations

import string as string_
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

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        a: dict[str, str] = dict.fromkeys(("a", "b", "rc"), "")
        f: dict[str, int] = dict.fromkeys(("a", "b", "rc"), -1)
        u: dict[str, int] = dict.fromkeys(("a", "b", "rc"), -1)
        o: Self
        s: str
        x: str
        y: str
        for s, o in info.items():
            if s == "":
                continue
            x = s.rstrip(string_.digits)
            if a == "":
                a = x
            elif a != x:
                raise ValueError
            y = s[len(x) :]
            if u[o.lit] == -1 or u[o.lit] > len(y):
                u[o.lit] = len(y)
            if not y.startswith("0"):
                continue
            if y == "0" and x[-1] in ".-_":
                continue
            if f[o.lit] == -1:
                f[o.lit] = len(y)
                continue
            if f[o.lit] != len(y):
                raise ValueError
        y = ""
        for x in ("a", "b", "rc"):
            if f[x] > u[x]:
                raise ValueError
            if a[x] == "":
                continue
            if f[x] == -1:
                f[x] = 0
            y += a[x]
            y += "#" * f[x]
        return y

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        return dict(matches=Cfg.cfg.fullmatches("pre_f", spec))

    def _format_parsed(self: Self, *, matches: dict) -> str:
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
