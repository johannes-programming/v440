from __future__ import annotations

import datahold
import keyalias

from v440._utils import QualifierParser
from v440._utils.Base import Base
from v440._utils.VList import VList

__all__ = ["Pre"]


@keyalias.keyalias(phase=0, subphase=1)
class Pre(VList):

    def __init__(self, data=None):
        self.data = data

    def __str__(self) -> str:
        if self.isempty():
            return ""
        return self.phase + str(self.subphase)

    @property
    def data(self) -> list:
        return list(self._data)

    @data.setter
    def data(self, value):
        self._data = QualifierParser.PRE(value)

    def isempty(self) -> bool:
        return self._data == [None, None]
