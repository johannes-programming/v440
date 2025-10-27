from __future__ import annotations

import string as string_
from typing import *

from v440._utils import forms
from v440._utils.forms import QualSpec
from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.QualStringer import QualStringer
from iterprod import iterprod

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
        specs:dict = dict()
        specs["a"] = QualSpec("", 0)
        specs["b"] = QualSpec("", 0)
        specs["rc"] = QualSpec("", 0)
        s:str
        o:Self
        for s, o in info.items():
            if not o:
                continue
            specs[o.lit] &= QualSpec.by_string(s)
        opts:dict = dict()
        opts["a"] = specs["a"].options(hollow="a", short="a")
        opts["b"] = specs["b"].options(hollow="b", short="b")
        opts["rc"] = specs["rc"].options(hollow="rc", short="c")
        a:str
        b:str
        c:str
        p:dict
        ans:list[str] = list()
        for a,b,c in iterprod(specs["a"], specs["b"], specs["rc"]):
            try:
                p = cls._format_parse(a + b + c)
                for s in ("a", "b", "rc"):
                    p[s] & specs[s]
            except Exception:
                continue
            else:
                ans.append(a + b + c)
        ans.sort()
        ans.sort(key=len)
        return ans[0]
    
    @classmethod
    def _format_parse(cls:type, spec:str, /) -> dict:
        m:dict = Cfg.fullmatches("pre_f", spec)
        ans:dict = dict()
        s:str
        for s in ("a", "b", "rc"):
            ans[s + "_spec"] = QualSpec(m[s + "_lit_f"], len(m[s + "_num_f"]))
        return ans

    def _format_parsed(
            self: Self, 
            *, 
            a_spec:QualSpec,
            b_spec:QualSpec,
            rc_spec:QualSpec,
    ) -> str:
        spec:QualSpec
        if self.lit == "a":
            spec = a_spec
        elif self.lit == "b":
            spec = b_spec
        elif self.lit == "rc":
            spec = rc_spec
        else:
            return ""
        if spec.head == "":
            return self.lit + str(self.num)
        if self.num or spec.mag or spec.head[-1] in tuple(".-_"):
            return spec.head + format(self.num, f"0{spec.mag}d")
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
