from abc import abstractmethod
from typing import Any, Self, cast

import cmp3
import setdoc
from datarepr import datarepr

from v440.abc.NonListABC import NonListABC

__all__ = ["NestedABC"]


class NestedABC(NonListABC):
    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(map(bool, self._todict().values()))

    @setdoc.basic
    def __cmp__(self: Self, other: Any) -> None | float | int:
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, **self._todict())

