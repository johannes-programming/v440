from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Digest import Digest
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard
from v440.core.Release import Release
from overloadable import Overloadable

__all__ = ["Base"]


parse_epoch: Digest = Digest("parse_epoch")


@parse_epoch.overload()
def parse_epoch() -> int:
    return 0


@parse_epoch.overload(int)
def parse_epoch(value: int) -> int:
    if value < 0:
        raise ValueError
    return value


@parse_epoch.overload(str)
def parse_epoch(value: str) -> int:
    s: str = value
    if s.endswith("!"):
        s = s[:-1]
    if s == "":
        return 0
    ans: int = int(s)
    if ans < 0:
        raise ValueError
    return ans


class Base(SlotList):

    __slots__ = ("_epoch", "_release")

    epoch: int
    release: Release
    string: str


    @Overloadable
    def __init__(self:Self, *args:Any, **kwargs:Any) -> bool:
        if len(args) == 1 and len(kwargs) == 0:
            return True
        if len(args) == 0 and "string" in kwargs.keys():
            return True
        return False
    
    @__init__.overload(True)
    @setdoc.basic
    def __init__(self: Self, string:Any) -> None:
        self._init_setup()
        self.string = string
    
    @__init__.overload(False)
    @setdoc.basic
    def __init__(self: Self, epoch:Any=None, release:Any=None)->Any:
        self._init_setup()
        self.epoch=epoch
        self.release = release

    def _format(self: Self, format_spec: str) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += format(self.release, format_spec)
        return ans
    
    def _init_setup(self:Self) -> None:
        self._epoch = 0
        self._release = Release()

    def _string_fset(self:Self, value:str) -> None:
        if "!" not in value:
            self._epoch = 0
            self.release.string = value
            return
        self.epoch, self.release.string=value.split("!")

    @property
    def epoch(self: Self) -> int:
        "This property represents the epoch."
        return self._epoch

    @epoch.setter
    @guard
    def epoch(self: Self, value: Any) -> None:
        self._epoch = parse_epoch(value)

    @property
    def release(self: Self) -> Release:
        "This property represents the release."
        return self._release

    @release.setter
    @guard
    def release(self: Self, value: Any) -> None:
        self._release.data = value

