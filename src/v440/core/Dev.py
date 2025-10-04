from __future__ import annotations

import string as string_
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.QualStringer import QualStringer

__all__ = ["Dev"]


class Dev(QualStringer):

    __slots__ = ()
    string: str
    phase: str
    num: int

    def _cmp(self: Self) -> tuple:
        return float("inf") if self.phase else self.num

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        if self.phase:
            return "." + self.phase + str(self.num)
        else:
            return ""

    def _num_fset(self: Self, value: int) -> None:
        if value < 0:
            raise ValueError
        if self.phase:
            self._num = value
        else:
            self.string = str(value)

    def _phase_fset(self: Self, value: str) -> None:
        if self.num and not value:
            self.string = str(self.num)
            return
        self._phase = Cfg.cfg.data["dev"][value.lower()]

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self._phase = ""
            self._num = 0
            return
        y: str = value.lower().replace("_", ".").replace("-", ".")
        x: str = y.rstrip(string_.digits)
        y = y[len(x) :]
        if x.endswith("."):
            x = x[:-1]
            if not y:
                raise ValueError
        if x.startswith("."):
            x = x[1:]
            if not x:
                raise ValueError
        self.phase = x
        self._num = int("0" + y)
