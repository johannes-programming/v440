from __future__ import annotations


from typing import *


from v440._utils.VList import VList
from v440._utils import utils

from v440.core.Release import Release
import keyalias


calc:utils.Digest = utils.Digest("calc")
@calc.overload()
def calc() -> list:
    return [0, 0]
@calc.overload(int)
def calc(value:int)->list:
    return [0, value]
@calc.overload(list)
def calc(value:list)->list:
    return value
@calc.overload(str)
def calc(value:str)->list:
    if "!" in value:
        return value.split("!")
    else:
        return [0, value]

@keyalias.keyalias(epoch=0, release=1)
class Base(VList):
    data: list
    epoch: int
    release: Release

    def __init__(self: Self, data: Any = None) -> None:
        self._data = [0, Release()]
        self.data = data

    def __str__(self: Self) -> str:
        if self.epoch:
            return "%s!%s" % tuple(self)
        else:
            return str(self.release)
        
    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        x:Any
        y:Any
        x, y = calc(value)
        if x < 0:
            raise ValueError
        self._data[0] = x
        self._data[1].data = y

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        return ans