from functools import partial
from typing import *

import setdoc

from v440._utils.BaseList import BaseList
from overloadable import Overloadable

__all__ = ["SlotList"]


class SlotList(BaseList):
    __slots__ = ()

    data: tuple

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(self.data)
        

    def _cmp(self: Self) -> tuple:
        return tuple(map(partial(getattr, self), type(self).__slots__))
