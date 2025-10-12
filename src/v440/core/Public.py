from __future__ import annotations

import string as string_
import sys
from typing import *

import setdoc

from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Base import Base
from v440.core.Qual import Qual

__all__ = ["Public"]


class Public(SlotStringer):

    __slots__ = ("_base", "_qual")

    string: str
    packaging: str
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
        f: tuple = self._split(format_spec)
        ans: str = format(self.base, f[0]) + format(self.qual, f[1])
        return ans

    @classmethod
    def _split(cls: type, value: str) -> tuple[str, str]:
        i: int = int(value.startswith("v"))
        while i < len(value):
            if value[i] in (string_.digits + "!."):
                i += 1
            else:
                break
        if value[:i].endswith("."):
            i -= 1
        return value[:i], value[i:]

    def _string_fset(self: Self, value: str) -> None:
        self.base.string, self.qual.string = self._split(value)

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
