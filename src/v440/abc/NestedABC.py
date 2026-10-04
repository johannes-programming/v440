"""Provide the NestedABC abstract base for v440 nested classes."""

from __future__ import annotations

__all__: list[str] = ["NestedABC"]

from abc import abstractmethod
from typing import Any, Self, cast

import cmp3
import setdoc
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC


class NestedABC(cmp3.CmpABC, CoreABC):
    """Provide comparison and representation behavior for nested version components."""

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self, /) -> bool:
        """Return whether this instance contains a meaningful value."""
        return any(map(bool, self._todict().values()))

    @setdoc.basic
    def __cmp__(self: Self, other: Any, /) -> None | float | int:
        """Compare this instance with another instance of the same concrete type."""
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    @setdoc.basic
    def __repr__(self: Self, /) -> str:
        """Return a reconstructive representation of this value."""
        return datarepr(type(self).__name__, **self._todict())

    @abstractmethod
    def _cmp(self: Self, /) -> Any: ...

    @classmethod
    @abstractmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]: ...

    def _init_other(self: Self, other: Self | None, /) -> None:
        """Initialize internal fields from a source value or their defaults."""
        field_name: str
        factory: Any
        for field_name, factory in self._init_factories().items():
            if other is None:
                setattr(self, field_name, factory())
            else:
                setattr(self, field_name, factory(getattr(other, field_name)))

    @abstractmethod
    def _todict(self: Self, /) -> dict[str, Any]: ...
