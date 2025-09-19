from __future__ import annotations

from typing import *

import packaging.version

from v440._utils.Digest import Digest
from v440._utils.WList import WList
from v440.core.Local import Local
from v440.core.Public import Public

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


class Version(WList):
    __slots__ = ("_public", "_local")
    
    data: list
    local: Local
    public: Public

    def __init__(self: Self, data: Any = "0", /, **kwargs: Any) -> None:
        self._public = Public()
        self._local = Local()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def _data(self: Self) -> tuple:
        return self.public, self.local

    @_data.setter
    def _data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = self.public.format(cutoff)
        if self.local:
            ans += "+%s" % self.local
        return ans

    def isempty(self:Self) -> bool:
        return self.public.isempty() and self.local.isempty()
    
    @property
    def local(self: Self) -> Local:
        return self._local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Self:
        return self._public

    @public.setter
    def public(self: Self, value: Any) -> None:
        self.public.data = value
