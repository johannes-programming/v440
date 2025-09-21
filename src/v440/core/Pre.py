from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Cfg import Cfg
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard

__all__ = ["Pre"]


parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return [None, None]


@parse_data.overload(list)
def parse_data(value: list) -> Any:
    l: Any
    n: Any
    l, n = list(map(utils.segment, value))
    if [l, n] == [None, None]:
        return [None, None]
    l = Cfg.cfg.data["phases"][l]
    if not isinstance(n, int):
        raise TypeError
    return [l, n]


@parse_data.overload(str)
def parse_data(value: str) -> list:
    if value == "":
        return [None, None]
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = Cfg.cfg.data["phases"][l]
    n = 0 if (n is None) else int(n)
    return [l, n]


class Pre(SlotList):

    __slots__ = ("_phase", "_subphase")

    data: list
    phase: Optional[str]
    subphase: Optional[int]

    def __init__(self: Self, data: Any = None) -> None:
        self._phase = None
        self._subphase = None
        self.data = data

    def __str__(self: Self) -> str:
        ans: str = ""
        if not self.isempty():
            ans += self.phase
            ans += str(self.subphase)
        return ans

    @property
    def data(self: Self) -> list:
        return [self._phase, self._subphase]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self._phase, self._subphase = parse_data(value)

    def isempty(self: Self) -> bool:
        return self.data == [None, None]

    @property
    def phase(self: Self) -> Optional[str]:
        return self._phase

    @phase.setter
    def phase(self: Self, value: Any) -> None:
        self[0] = value

    @property
    def subphase(self: Self) -> Optional[int]:
        return self._subphase

    @subphase.setter
    def subphase(self: Self, value: Any) -> None:
        self[1] = value
