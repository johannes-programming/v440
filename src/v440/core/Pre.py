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
            return phase + str(num)
        else:
            return ""

    def _num_fset(self: Self, value: int) -> None:
        if value < 0:
            raise ValueError
        self.string = self.phase + str(value)

    @classmethod
    def _phasedict(cls: type) -> dict:
        return Cfg.cfg.data["pre"]

    def _string_fset(self: Self, value: str) -> None:
        self._phase, self._num = self._string_parse_common(value)
