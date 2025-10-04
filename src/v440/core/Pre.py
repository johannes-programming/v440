from __future__ import annotations

import string as string_
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.QualStringer import QualStringer

__all__ = ["Pre"]


class Pre(QualStringer):

    __slots__ = ()
    string: str
    phase: str
    num: int

    def _cmp(self: Self) -> tuple:
        return {bool(self)}, self.phase, self.num

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        if self:
            return self.phase + str(self.num)
        else:
            return ""

    def _num_fset(self: Self, value: int) -> None:
        if value < 0:
            raise ValueError
        self.string = self.phase + str(value)

    def _phase_fset(self: Self, value: str) -> None:
        if value:
            self._phase = Cfg.cfg.data["pre"][value.lower()]
        elif self.num:
            self.string = str(self.num)
        else:
            self._phase = ""

    def _string_fset(self: Self, value: str) -> None:
        v: str = value.lower()
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        x: str = v.rstrip(string_.digits)
        v = v[len(x) :]
        q: bool = x.endswith(".")
        if q:
            if not v:
                raise ValueError
            x = x[:-1]
        p: bool = x.startswith(".")
        if p:
            x = x[1:]
        if x:
            self._phase = Cfg.cfg.data["pre"][x]
            self._num = int("0" + v)
        elif p or v:
            raise ValueError
        else:
            self._phase = ""
            self._num = 0
