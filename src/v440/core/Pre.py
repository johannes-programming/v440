from __future__ import annotations

import keyalias

from v440._utils import QualifierParser
from v440._utils.VList import VList
from typing import *

__all__ = ["Pre"]


@keyalias.keyalias(phase=0, subphase=1)
class Pre(VList):

    def __init__(self:Self, data:Any=None)->None:
        self.data = data

    def __str__(self:Self) -> str:
        if self.isempty():
            return ""
        return self.phase + str(self.subphase)

    @property
    def data(self:Self) -> list:
        return list(self._data)

    @data.setter
    def data(self:Self, value:Any)->None:
        self._data = QualifierParser.PRE(value)

    def isempty(self:Self) -> bool:
        return self._data == [None, None]
