from functools import partial
from typing import *

import setdoc
from datarepr import datarepr
from frozendict import frozendict
from abc import abstractmethod

from v440._utils.BaseList import BaseList

__all__ = ["SlotList"]


class SlotList(BaseList):
    __slots__ = ()

    data: frozendict

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(self.data)

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(type(self).__slots__)
    
    @setdoc.basic
    def __repr__(self:Self)-> str:
        return datarepr(type(self).__name__, **self.data)

    def _cmp(self: Self) -> tuple:
        return tuple(map(partial(getattr, self), type(self).__slots__))
    
    @property
    @abstractmethod
    @setdoc.basic
    def data(self: Self) -> frozendict: ...