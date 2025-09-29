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

    data: tuple
    string: str
    local: Local
    public: Public

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self._public = Public()
        self._local = Local()
        self.data = data

    def _format(self: Self, format_spec: str) -> str:
        ans: str = format(self.public, format_spec)
        if self.local:
            ans += "+" + format(self.local)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        parsed: Iterable
        if "+" in value:
            parsed = value.split("+")
        else:
            parsed = value, ""
        self.public.string, self.local.string = parsed

    @property
    @setdoc.basic
    def data(self: Self) -> tuple:
        return self.public, self.local

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    @property
    def local(self: Self) -> Local:
        "This property represents the local identifier."
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
        "This property represents the public identifier."
        return self._public

    @public.setter
    @guard
    def public(self: Self, value: Any) -> None:
        self.public.data = value
