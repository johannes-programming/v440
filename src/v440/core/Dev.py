from __future__ import annotations

import operator
from typing import *

from v440._utils import forms
from v440._utils.Cfg import Cfg
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
        Cfg.fullmatches("dev_f", spec)
        return dict(spec=spec)

    def _format_parsed(self: Self, *, spec: str) -> str:
        if not self:
            return ""
        elif not spec:
            return ".dev" + str(self.num)
        else:
            return forms.qualform(spec, self.num)

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
