from __future__ import annotations

import dataclasses
from typing import *

import packaging.version
from catchlib import Catcher

from v440._utils import utils
from v440._utils.VList import VList
from v440.core.Local import Local
from v440.core.Public import Public
from v440.core.VersionError import VersionError

parse_data: utils.Digest = utils.Digest("parse_data")


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


class Version(VList):

    __slots__ = ("_public", "_local")
    data: list
    public: Public
    local: Local

    def __init__(self: Self, data: Any = None) -> None:
        self._public = Public()
        self._local = Local()
        self.data = data

    def __str__(self: Self) -> str:
        return self.format()

    @property
    def data(self: Self) -> str:
        return [self.public, self.local]

    @data.setter
    def data(self: Self, value: Any) -> None:
        self.public, self.local = parse_data(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = self.public.format(cutoff)
        if not self.local.isempty():
            ans += "+%s" % self.local
        return ans

    @property
    def local(self: Self) -> Public:
        return self._local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Public:
        return self._public

    @public.setter
    def public(self: Self, value: Any) -> None:
        self.public.data = value
