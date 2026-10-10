"""Provide the ListABC abstract base for list-like v440 classes."""

from __future__ import annotations

__all__: list[str] = ["ListABC"]

from abc import abstractmethod
from collections import abc
from functools import cmp_to_key
from typing import Any, Self, SupportsIndex, TypeVar

import setdoc
from datahold import BaseDataObject, HoldList

from v440._utils.list_key import list_key
from v440._utils.setter import setter
from v440.abc.CoreABC import CoreABC

Item = TypeVar("Item", bound=int | str)


class ListABC(HoldList[Item], CoreABC):
    """Define shared sequence behavior for list-like version components."""

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self, /) -> bool:
        """Return whether this sequence contains any normalized components."""
        return bool(self.data)

    __eq__ = BaseDataObject.__eq__

    @setdoc.basic
    def __ge__(self: Self, other: object, /) -> Any:
        """Compare this sequence with another data object using PEP 440 item ordering."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__ge__(self, other)
        return tuple(map(list_key, self)) >= tuple(map(list_key, other))

    @setdoc.basic
    def __gt__(self: Self, other: object, /) -> Any:
        """Compare this sequence with another data object using PEP 440 item ordering."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__gt__(self, other)
        return tuple(map(list_key, self)) > tuple(map(list_key, other))

    @setdoc.basic
    def __init__(
        self: Self,
        other: abc.Iterable[Item] | None = None,
        /,
        **kwargs: Any,
    ) -> None:
        """Initialize this sequence from an iterable and keyword overrides."""
        self._init_other(other)
        self._init_kwargs(**kwargs)

    @setdoc.basic
    def __le__(self: Self, other: object, /) -> Any:
        """Compare this sequence with another data object using PEP 440 item ordering."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__le__(self, other)
        return tuple(map(list_key, self)) <= tuple(map(list_key, other))

    @setdoc.basic
    def __lt__(self: Self, other: object, /) -> Any:
        """Compare this sequence with another data object using PEP 440 item ordering."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__lt__(self, other)
        return tuple(map(list_key, self)) < tuple(map(list_key, other))

    __repr__ = HoldList.__repr__

    @classmethod
    @abstractmethod
    def _data_parse(
        cls: type[Self],
        /,
        *value: Any,
    ) -> abc.Iterable[Item]: ...

    def _init_other(self: Self, other: abc.Iterable[Item] | None, /) -> None:
        """Initialize sequence data from an optional iterable."""
        self._data = ()
        if other is not None:
            self.data = other

    @property
    @setdoc.basic
    def data(self: Self, /) -> tuple[Item, ...]:
        """Return the normalized immutable sequence data."""
        return self._data

    @data.setter
    @setter
    def data(self: Self, value: abc.Iterable[Any], /) -> None:
        """Replace sequence data after normalizing every supplied item."""
        self._data = tuple(self._data_parse(*value))

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        """Sort the normalized sequence data in place."""
        self.data = sorted(
            self,
            key=cmp_to_key(cmp) if key is None else key,
            reverse=reverse,
        )


def cmp(x: Any, y: Any) -> Any:
    """Compare two values with PEP 440 style for mixed int/str."""
    type_order: int
    if x is y or x == y:
        return 0
    try:
        if x <= y:
            return -1
        else:
            return 1
    except Exception:
        type_order = bool(isinstance(x, int)) - bool(isinstance(y, int))
        if type_order == 0:
            raise
        else:
            return type_order
