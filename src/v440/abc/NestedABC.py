"""Provide the NestedABC abstract base for v440 nested classes."""

__all__: list[str] = ["NestedABC"]

from abc import abstractmethod
from typing import Any, Self, cast

import cmp3
import setdoc
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC


class NestedABC(cmp3.CmpABC, CoreABC):
    """Represent NestedABC."""

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self, /) -> bool:
        """Handle bool."""
        return any(map(bool, self._todict().values()))

    @setdoc.basic
    def __cmp__(self: Self, other: Any, /) -> None | float | int:
        """Handle cmp."""
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    @setdoc.basic
    def __repr__(self: Self, /) -> str:
        """Handle repr."""
        return datarepr(type(self).__name__, **self._todict())

    @abstractmethod
    def _cmp(self: Self, /) -> Any: ...

    @classmethod
    @abstractmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]: ...

    def _init_other(self: Self, other: Self | None, /) -> None:
        """Handle init other."""
        x: str
        y: Any
        for x, y in self._init_factories().items():
            if other is None:
                setattr(self, x, y())
            else:
                setattr(self, x, y(getattr(other, x)))

    @abstractmethod
    def _todict(self: Self, /) -> dict[str, Any]: ...
