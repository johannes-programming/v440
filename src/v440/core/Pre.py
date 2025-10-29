from __future__ import annotations

from typing import *

from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.Eden import Eden
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
        a: str
        b: str
        c: str
        s: str
        o: Self
        matches: dict[str, str]
        opts: list[set]
        specs: list[Eden]
        sols: list
        specs = [Eden()] * 3
        for s, o in info.items():
            if not o:
                continue
            specs[("a", "b", "rc").index(o.lit)] &= Eden.by_example(s)
        opts = list()
        opts.append(specs[0].options(hollow="a", short="a"))
        opts.append(specs[1].options(hollow="b", short="b"))
        opts.append(specs[2].options(hollow="rc", short="c"))
        sols = list()
        for a, b, c in iterprod(*opts):
            s = a + b + c
            try:
                matches = Cfg.fullmatches("pre_f", s)
                specs[0] & Eden.by_spec(matches["a_f"])
                specs[1] & Eden.by_spec(matches["b_f"])
                specs[2] & Eden.by_spec(matches["rc_f"])
            except Exception:
                continue
            else:
                sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        m: dict
        ans: dict
        m = Cfg.fullmatches("pre_f", spec)
        ans = dict()
        ans["a"] = Eden.by_spec(m["a_f"])
        ans["b"] = Eden.by_spec(m["b_f"])
        ans["rc"] = Eden.by_spec(m["rc_f"])
        return ans

    def _format_parsed(self: Self, *, a: Eden, b: Eden, rc: Eden) -> str:
        ans: str
        eden: Eden
        if self.lit == "a":
            eden = a
        elif self.lit == "b":
            eden = b
        elif self.lit == "rc":
            eden = rc
        else:
            return ""
        if eden.head == "":
            return self.lit + str(self.num)
        ans = eden.head
        if eden.sep != "?":
            ans += eden.sep
        if self.num or eden.mag:
            ans += format(self.num, f"0{eden.mag}d")
        return ans

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        return Cfg.cfg.data["consts"]["phases"][value]

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
