"""Provide the NestedABC abstract base for v440 nested classes."""

from __future__ import annotations

__all__: list[str] = ["NestedABC"]

from abc import abstractmethod
from typing import Any, Self, cast

import cmp3
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC


class NestedABC(cmp3.CmpABC, CoreABC):
    """Define shared comparison and representation behavior for nested version components."""

    __slots__ = ()

    def __bool__(self: Self, /) -> bool:
        """Do bool(self)."""
        return any(map(bool, self._todict().values()))

    def __cmp__(self: Self, other: Any, /) -> None | float | int:
        """Compare compatible nested objects through their normalized comparison keys."""
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    def __repr__(self: Self, /) -> str:
        """Do repr(self)."""
        return datarepr(type(self).__name__, **self._todict())

    @abstractmethod
    def _cmp(self: Self, /) -> Any:
        "..."

    @classmethod
    @abstractmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        "..."

    def _init_other(self: Self, other: Self | None, /) -> None:
        """Initialize nested fields from defaults or a compatible source object."""
        attribute: str
        factory: Any
        for attribute, factory in self._init_factories().items():
            if other is None:
                setattr(self, attribute, factory())
            else:
                setattr(self, attribute, factory(getattr(other, attribute)))

    @abstractmethod
    def _todict(self: Self, /) -> dict[str, Any]:
        "..."
