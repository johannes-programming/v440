"""Provide the ListABC abstract base for list-like v440 classes."""

from __future__ import annotations

__all__: list[str] = ["ListABC"]

from abc import abstractmethod
from collections import abc
from functools import cmp_to_key
from typing import Any, Self, TypeVar

import setdoc
from datahold import BaseDataObject, HoldList

from v440._utils.setter import setter
from v440.abc.CoreABC import CoreABC

Item = TypeVar("Item", bound=int | str)


class ListABC(HoldList[Item], CoreABC):
    """Provide list-like storage, comparison, and mutation for version components."""

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self, /) -> bool:
        """Return whether this instance contains a meaningful value."""
        return bool(self.data)

    __eq__ = BaseDataObject.__eq__

    @setdoc.basic
    def __ge__(self: Self, other: object, /) -> Any:
        """Return whether this value sorts at or after the other value."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__ge__(self, other)
        return tuple(map(cmpkey, self)) >= tuple(map(cmpkey, other))

    @setdoc.basic
    def __gt__(self: Self, other: object, /) -> Any:
        """Return whether this value sorts after the other value."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__gt__(self, other)
        return tuple(map(cmpkey, self)) > tuple(map(cmpkey, other))

    @setdoc.basic
    def __init__(
        self: Self,
        other: abc.Iterable[Item] | None = None,
        /,
        **kwargs: Any,
    ) -> None:
        """Initialize this value from an optional source and keyword overrides."""
        self._init_other(other)
        self._init_kwargs(**kwargs)

    @setdoc.basic
    def __le__(self: Self, other: object, /) -> Any:
        """Return whether this value sorts at or before the other value."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__le__(self, other)
        return tuple(map(cmpkey, self)) <= tuple(map(cmpkey, other))

    @setdoc.basic
    def __lt__(self: Self, other: object, /) -> Any:
        """Return whether this value sorts before the other value."""
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__lt__(self, other)
        return tuple(map(cmpkey, self)) < tuple(map(cmpkey, other))

    __repr__ = HoldList.__repr__

    @classmethod
    @abstractmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> abc.Iterable[Item]: ...

    def _init_other(self: Self, other: abc.Iterable[Item] | None, /) -> None:
        """Initialize internal fields from a source value or their defaults."""
        self._data = ()
        if other is not None:
            self.data = other

    @property
    @setdoc.basic
    def data(self: Self, /) -> tuple[Item, ...]:
        """Return the normalized sequence data."""
        return self._data

    @data.setter
    @setter
    def data(self: Self, value: abc.Iterable[Any], /) -> None:
        """Validate and replace the normalized sequence data."""
        self._data = tuple(self._data_parse(list(value)))

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        "Sort the data."
        self.data = sorted(
            self,
            key=cmp_to_key(cmp) if key is None else key,
            reverse=reverse,
        )


def cmp(left: Any, right: Any) -> Any:
    """Compare two values with PEP 440 style for mixed int/str."""
    type_order: int
    if left is right or left == right:
        return 0
    try:
        if left <= right:
            return -1
        else:
            return 1
    except Exception:
        type_order = bool(isinstance(left, int)) - bool(isinstance(right, int))
        if type_order == 0:
            raise
        else:
            return type_order


def cmpkey(item: int | str, /) -> tuple[bool, int | str]:
    """Return key for sorting int before str."""
    return isinstance(item, int), item
