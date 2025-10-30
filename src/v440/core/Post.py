from __future__ import annotations

import operator
from typing import *

from v440._utils import forms
from v440._utils.Cfg import Cfg
from v440._utils.Eden import Eden
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

    @classmethod
    def _deformat(cls: type, info: dict, /) -> str:
        return forms.qualdeform(*info.keys(), hollow=".post")

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> str:
        m: dict
        e: Eden
        m = Cfg.fullmatches("post_f", spec)
        e = Eden(
            head=m["post_head_f"] or m["post_hyphen_f"],
            sep=m["post_sep_f"],
            mag=len(m["post_num_f"]),
        )
        return dict(eden=e)

    def _format_parsed(self: Self, *, eden: Eden) -> str:
        if not self:
            return ""
        if "" == eden.head:
            return ".post" + str(self.num)
        if 0 == eden.mag and 0 == self.num and "-" != eden.head:
            return eden.head
        return eden.head + eden.sep + format(self.num, f"0{eden.mag}d")

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
