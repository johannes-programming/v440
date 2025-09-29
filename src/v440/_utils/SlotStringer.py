from functools import partial
from typing import *

import setdoc
from datarepr import datarepr

from v440._utils.BaseStringer import BaseStringer

__all__ = ["SlotList"]


class SlotStringer(BaseStringer):
    __slots__ = ()

    string: str

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, **self._todict())

    def _cmp(self: Self) -> tuple:
        return tuple(map(partial(getattr, self), type(self).__slots__))

    def _set(self: Self, value: Any) -> None:
        if value is None:
            self.string = ""
        else:
            self.string = value
