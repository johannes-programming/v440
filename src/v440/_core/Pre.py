from __future__ import annotations

import datahold
import keyalias

from v440._core import Parser

from v440._core import utils

__all__ = ["Pre"]


@keyalias.keyalias(phase=0, subphase=1)
class Pre(datahold.OkayList):

    __ge__ = utils.Base.__ge__

    def __init__(self, data=None):
        self.data = data

    __le__ = utils.Base.__le__

    __repr__ = utils.Base.__repr__

    def __str__(self) -> str:
        if self.isempty():
            return ""
        return self.phase + str(self.subphase)

    @utils.proprietary
    class data:
        def getter(self) -> list:
            return list(self._data)
        @utils.setterdeco
        def setter(self, value, /):
            self._data = Parser.PRE.parse(value)

    def isempty(self):
        return self._data == [None, None]
