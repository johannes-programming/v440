from __future__ import annotations

from typing import *

import packaging.version
import setdoc

from v440._utils.Digest import Digest
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard
from v440.core.Local import Local
from v440.core.Public import Public

__all__ = ["Version"]

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
    if "+" in value:
        return tuple(value.split("+"))
    else:
        return value, None


class Version(SlotList):
    __slots__ = ("_public", "_local")

    data: list
    local: Local
    public: Public

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self._public = Public()
        self._local = Local()
        self.data = data

    @setdoc.basic
    def __str__(self: Self) -> str:
        return self.format()

    @property
    @setdoc.basic
    def data(self: Self) -> list:
        return [self.public, self.local]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = self.public.format(cutoff)
        if self.local:
            ans += "+%s" % self.local
        return ans

    @property
    def local(self: Self) -> Local:
        return self._local

    @local.setter
    @guard
    def local(self: Self, value: Any) -> None:
        self.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Self:
        return self._public

    @public.setter
    @guard
    def public(self: Self, value: Any) -> None:
        self.public.data = value
