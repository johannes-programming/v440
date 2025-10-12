from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Base import Base
from v440.core.Qual import Qual
import string as string_

__all__ = ["Public"]


class Public(SlotStringer):

    __slots__ = ("_base", "_qual")

    string: str
    base: Base
    qual: Qual

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._base = Base()
        self._qual = Qual()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.base, self.qual

    def _format(self: Self, format_spec: str) -> str:
        return format(self.base, format_spec) + format(self.qual)

    def _string_fset(self: Self, value: str) -> None:
        i:int = int(value.startswith("v"))
        while i < len(value):
            if value[i] in (string_.digits + "!."):
                i += 1
            else:
                break
        if i and (value[i] == "."):
            i -= 1
        self.base.string = value[:i]
        self.qual.string = value[i:]

    def _todict(self: Self) -> dict:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual
