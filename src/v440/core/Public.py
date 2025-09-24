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


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> tuple:
    return None, None


@parse_data.overload(int)
def parse_data(value: int) -> tuple:
    return value, None


@parse_data.overload(list)
def parse_data(value: list) -> tuple:
    return tuple(value)


@parse_data.overload(str)
def parse_data(value: str) -> tuple:
    match: Any = Pattern.PUBLIC.leftbound.search(value)
    return value[: match.end()], value[match.end() :]


class Public(SlotList):

    __slots__ = ("_base", "_qual")

    data: list
    base: Base
    qual: Qual

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self._base = Base()
        self._qual = Qual()
        self.data = data

    def _format(self: Self, format_spec: str) -> str:
        return format(self.base, format_spec) + format(self.qual)

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @base.setter
    @guard
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    @setdoc.basic
    def data(self: Self) -> list:
        return [self.base, self.qual]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.base, self.qual = parse_data(value)

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual

    @qual.setter
    @guard
    def qual(self: Self, value: Any) -> None:
        self.qual.data = value
