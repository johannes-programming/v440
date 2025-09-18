from __future__ import annotations

from typing import *

import keyalias

from v440._utils import QualifierParser
from v440._utils.VList import VList
from v440._utils import utils
from v440.core.Pre import Pre

__all__ = ["Qualification"]

parse_data:utils.Digest = utils.Digest()

@keyalias.keyalias(phase=0, subphase=1)
class Qualification(VList):

    data: list
    pre: Pre
    post:Optional[int]
    dev:Optional[int]


    def __init__(self: Self, data: Any = None) -> None:
        self.data = data

    def __str__(self: Self) -> str:
        ans: str = ""
        if not self.isempty():
            ans += self.phase
            ans += str(self.subphase)
        return ans

    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        self._data = QualifierParser.PRE(value)

    def isempty(self: Self) -> bool:
        return self._data == [None, None]
