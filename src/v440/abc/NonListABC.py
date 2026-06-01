from abc import abstractmethod
from typing import Any, Self, cast, overload

import cmp3
import setdoc

from v440.abc.CoreABC import CoreABC

__all__ = ["NonListABC"]


class NonListABC(cmp3.CmpABC, CoreABC):
    __slots__ = ()

    @setdoc.basic
    def __cmp__(self: Self, other: Any) -> None | float | int:
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    @overload
    @abstractmethod
    @setdoc.basic
    def __init__(self: Self) -> None: ...

    @overload
    @abstractmethod
    @setdoc.basic
    def __init__(self: Self, string: object) -> None: ...

    @abstractmethod
    def _cmp(self: Self) -> Any: ...
