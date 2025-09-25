import collections
from abc import abstractmethod
from functools import partial
from typing import *

import scaevola
import setdoc
from datarepr import datarepr

from v440._utils.BaseList import BaseList
from v440._utils.utils import guard
from v440.core.VersionError import VersionError

__all__ = ["SlotList"]


@scaevola.auto
class SlotList(collections.abc.Collection, BaseList):
    __slots__ = ()

    data: tuple

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(self.data)

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(type(self).__slots__)

    def _cmp(self: Self) -> tuple:
        return tuple(map(partial(getattr, self), type(self).__slots__))
