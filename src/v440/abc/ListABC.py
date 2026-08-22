"""Provide the ListABC abstract base for list-like v440 classes."""

__all__: list[str] = ["ListABC"]

import contextlib
import functools
from abc import abstractmethod
from collections import abc
from functools import cmp_to_key
from typing import Any, Optional, Self

import setdoc
from datahold import MutableListSlot

from v440.abc.CoreABC import CoreABC


class ListABC[Item: int | str](MutableListSlot[Item], CoreABC):

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self, /) -> bool:
        return bool(self.data)

    @setdoc.basic
    @functools.wraps(MutableListSlot.__ge__)
    def __ge__(self: Self, other: Any, /) -> bool:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) >= tuple(map(cmpkey, other))
        else:
            return MutableListSlot.__ge__(self, other)

    @setdoc.basic
    @functools.wraps(MutableListSlot.__gt__)
    def __gt__(self: Self, other: Any, /) -> bool:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) > tuple(map(cmpkey, other))
        else:
            return MutableListSlot.__gt__(self, other)

    @setdoc.basic
    def __init__(
        self: Self,
        data: Optional[abc.Iterable[Item]] = None,
        /,
        **kwargs: Any,
    ) -> None:
        self._data = ()
        if data is not None:
            self.data = data
        self._init_kwargs(**kwargs)

    @setdoc.basic
    @functools.wraps(MutableListSlot.__le__)
    def __le__(self: Self, other: Any, /) -> bool:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) <= tuple(map(cmpkey, other))
        else:
            return MutableListSlot.__le__(self, other)

    @setdoc.basic
    @functools.wraps(MutableListSlot.__lt__)
    def __lt__(self: Self, other: Any, /) -> bool:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) < tuple(map(cmpkey, other))
        else:
            return MutableListSlot.__lt__(self, other)

    @contextlib.contextmanager
    @setdoc.basic
    def __mutate__(
        self: Self, /
    ) -> abc.Generator[list[int | str], None, None]:
        mutable: list[int | str]
        mutable = list(self._slot)
        yield mutable
        self._slot = tuple(self._data_parse(mutable))

    @classmethod
    def __type__(cls: type[Self], data: abc.Iterable[int | str], /) -> Self:
        return cls(data)

    @classmethod
    @abstractmethod
    def _data_parse(
        cls: type[Self], value: list[Any]
    ) -> abc.Iterable[Item]: ...

    @property
    @setdoc.basic
    def data(self: Self, /) -> tuple[Item, ...]:
        return self.__frozen__()

    @data.setter
    def data(self: Self, value: abc.Iterable[Any], /) -> None:
        with self.__mutate__() as mutable:
            mutable.clear()
            mutable.extend(value)

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        "Sort the data."
        self.data = sorted(
            self,
            key=cmp_to_key(cmp) if key is None else key,
            reverse=reverse,
        )


def cmp(x: Any, y: Any) -> Any:
    """Compare two values with PEP 440 style for mixed int/str."""
    i: int
    if x is y or x == y:
        return 0
    try:
        if x <= y:
            return -1
        else:
            return 1
    except Exception:
        i = bool(isinstance(x, int)) - bool(isinstance(y, int))
        if i == 0:
            raise
        else:
            return i


def cmpkey(x: int | str, /) -> tuple[bool, int | str]:
    """Return key for sorting int before str."""
    return isinstance(x, int), x
