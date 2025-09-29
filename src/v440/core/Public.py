from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard
from v440.core.Base import Base
from v440.core.Qual import Qual

__all__ = ["Public"]

class Public(SlotList):

    __slots__ = ("_base", "_qual")

    base: Base
    qual: Qual
    string: str

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self._base = Base()
        self._qual = Qual()
        self.data = data

    def _format(self: Self, format_spec: str) -> str:
        return format(self.base, format_spec) + format(self.qual)
    
    def _string_fset(self:Self, value:str)->None:
        match: Any = Pattern.PUBLIC.leftbound.search(value)
        self.base.string = value[: match.end()]
        self.qual.string = value[match.end() :]

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @base.setter
    @guard
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual

    @qual.setter
    @guard
    def qual(self: Self, value: Any) -> None:
        self.qual.data = value
