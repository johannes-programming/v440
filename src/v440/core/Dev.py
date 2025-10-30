from __future__ import annotations

import operator
from typing import *

from v440._utils import forms
from v440._utils.Cfg import Cfg
from v440._utils.Eden import Eden
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

    @classmethod
    def _deformat(cls: type, info: dict, /) -> str:
        return forms.qualdeform(*info.keys(), hollow=".dev")

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        m: dict
        e: Eden
        m = Cfg.fullmatches("dev_f", spec)
        e = Eden(
            head=m["dev_head_f"],
            sep=m["dev_sep_f"],
            mag=len(m["dev_num_f"]),
        )
        return dict(eden=e)

    def _format_parsed(self: Self, *, eden: Eden) -> str:
        if not self:
            return ""
        if "" == eden.head:
            return ".dev" + str(self.num)
        if 0 == eden.mag and 0 == self.num:
            return eden.head
        return eden.head + eden.sep + format(self.num, f"0{eden.mag}d")

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
