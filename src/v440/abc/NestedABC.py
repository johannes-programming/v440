from abc import abstractmethod
from typing import *

import cmp3  # type: ignore
import setdoc
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC

__all__ = ["NestedABC"]


class NestedABC(cmp3.CmpABC, CoreABC):
    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return any(map(bool, self._todict().values()))

    @setdoc.basic
    def __cmp__(self: Self, other: Any) -> None | float | int:
        if type(self) is not type(other):
            return None
        return cmp3.cmp(self._cmp(), other._cmp(), mode="le")

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, **self._todict())

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @abstractmethod
    def _todict(self: Self) -> dict[str, Any]: ...

    packaging = CoreABC.string
