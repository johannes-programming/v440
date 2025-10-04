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

    def _cmp(self: Self) -> float | int:
        if self.phase:
            return self.num
        else:
            return float("inf")

    @classmethod
    def _format_cls(
        cls: type,
        *,
        phase: str,
        num: int,
        format_spec: str = "",
    ) -> str:
        if format_spec:
            raise ValueError
        if phase:
            return "." + phase + str(num)
        else:
            return ""

    def _num_fset(self: Self, value: int) -> None:
        if value < 0:
            raise ValueError
        self.string = self._format_cls(phase=self.phase, num=value)

    @classmethod
    def _phasedict(cls: type) -> dict:
        return Cfg.cfg.data["dev"]

    def _string_fset(self: Self, value: str) -> None:
        self._phase, self._num = self._string_parse_common(value)
