from functools import partial
from typing import *

import setdoc

from v440._utils.BaseList import BaseList

__all__ = ["SlotList"]


class SlotList(BaseList):
    __slots__ = ()

    data: tuple
    string: str

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(self.data)

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(type(self).__slots__)

    def _cmp(self: Self) -> tuple:
        return tuple(map(partial(getattr, self), type(self).__slots__))
