from __future__ import annotations

from typing import *

from catchlib import Catcher

from v440._utils import utils
from v440._utils.VList import VList
from v440.core.Release import Release

__all__ = ["Base"]

parse_data: utils.Digest = utils.Digest()


@parse_data.overload()
def parse_data():
    return 0, []


@parse_data.overload(list)
def parse_data(value: list):
    return value


@parse_data.overload(int)
def parse_data(value: int):
    return 0, value


@parse_data.overload(str)
def parse_data(value: str):
    if "!" in value:
        return value.split("!")
    else:
        return 0, value


parse_epoch: utils.Digest = utils.Digest()


@parse_epoch.overload()
def parse_epoch():
    return 0


@parse_epoch.overload(int)
def parse_epoch(value: int):
    if value < 0:
        raise ValueError
    return value


@parse_epoch.overload(str)
def parse_epoch(value: str):
    return utils.numeral(value)


class Base(VList):

    __slots__ = "_data"
    data: list
    epoch: int
    release: Release

    def __init__(self: Self, data: Any = None) -> None:
        self.data = data

    def __str__(self: Self) -> str:
        if self.epoch:
            return "%s!%s" % tuple(self)
        else:
            return str(self.release)

    @property
    def data(self: Self) -> list:
        return self._data

    @data.setter
    @utils.vGuard
    def data(self: Self, value: Any) -> None:
        self.epoch, self.release.data = parse_data(value)

    @property
    def epoch(self: Self) -> int:
        return self._epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self._epoch = parse_epoch(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        return ans

    @property
    def release(self: Self) -> Release:
        return self._release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self.release.data = value
