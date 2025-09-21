from __future__ import annotations

from typing import *

import packaging.version

from v440._utils.Digest import Digest
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard
from v440.core.Base import Base
from v440.core.Local import Local
from v440.core.Public import Public
from v440.core.Qualification import Qualification
from v440.core.Release import Release

parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None]


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return [value, None]


@parse_data.overload(list)
def parse_data(value: list) -> list:
    return value


@parse_data.overload(str)
def parse_data(value: str) -> list:
    if "+" in value:
        return value.split("+")
    else:
        return [value, None]


class Version(SlotList):
    __slots__ = ("_public", "_local")
    base: Base
    data: list
    dev: Optional[int]
    epoch: int
    local: Local
    post: Optional[int]
    public: Public
    qualification: Qualification
    release: Release

    def __init__(self: Self, data: Any = "0") -> None:
        self._public = Public()
        self._local = Local()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def data(self: Self) -> list:
        return [self.public, self.local]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    @property
    def base(self: Self) -> Base:
        return self.public.base

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.base.data = value

    @property
    def dev(self: Self) -> Optional[int]:
        return self.qualification.dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self.qualification.dev = value

    @property
    def epoch(self: Self) -> int:
        return self.base.epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self.base.epoch = value

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
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Self:
        return self._public

    @public.setter
    @guard
    def public(self: Self, value: Any) -> None:
        self.public.data = value
