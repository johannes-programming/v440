from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Pattern import Pattern
from v440._utils.VList import VList
from v440.core.Base import Base
from v440.core.Pre import Pre
from v440.core.Qualification import Qualification

__all__ = ["Public"]

parse_data: utils.Digest = utils.Digest()


@parse_data.overload()
def parse_data() -> tuple:
    return None, None, None


@parse_data.overload(int)
def parse_data(value: int) -> tuple:
    return None, value, None


@parse_data.overload(list)
def parse_data(value: list) -> tuple:
    return tuple(value)


@parse_data.overload(str)
def parse_data(value: str) -> tuple:
    v: str = value
    pre = None
    post = None
    dev = None
    m: Any
    x: Any
    y: Any
    while v:
        m = Pattern.QUALIFIERS.leftbound.search(v)
        v = v[m.end() :]
        if m.group("N"):
            post = m.group("N")
            continue
        x = m.group("l")
        y = m.group("n")
        if x == "dev":
            dev = y
            continue
        if x in ("post", "r", "rev"):
            post = y
            continue
        pre = (x, y)
    return pre, post, dev


class Public(VList):

    __slots__ = ("_base", "_qualification")
    data: list
    base: Base
    qualification: Qualification

    def __init__(self: Self, data: Any = None) -> None:
        self._base = Base()
        self._qualification = Qualification()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def base(self: Self) -> Base:
        return self._base

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    def data(self: Self) -> list:
        return [self.base, self.qualification]

    @data.setter
    @utils.vGuard
    def data(self: Self, value: Any) -> None:
        self.base, self.qualification = parse_data(value)

    def format(self: Self, cutoff: Any = None) -> str:
        return self.base.format(cutoff) + str(self.qualification)

    @property
    def qualification(self: Self) -> Pre:
        return self._qualification

    @qualification.setter
    def qualification(self: Self, value: Any) -> None:
        self.qualification.data = value
