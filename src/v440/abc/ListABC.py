from abc import abstractmethod
from collections.abc import Iterable
from functools import cmp_to_key
from typing import Any, Final, Optional, Self, TypeVar

import setdoc
from datahold import BaseDataObject, HoldList
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC

__all__ = ["ListABC"]

Item = TypeVar("Item", bound=int | str)

MISSING: Final[object] = object()


def cmp(x: Any, y: Any) -> Any:
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
    return isinstance(x, int), x


class ListABC(CoreABC, HoldList[Item]):

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    __eq__ = BaseDataObject.__eq__

    @setdoc.basic
    def __ge__(self: Self, other: object) -> Any:
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__ge__(self, other)
        return tuple(map(cmpkey, self)) >= tuple(map(cmpkey, other))

    @setdoc.basic
    def __gt__(self: Self, other: object) -> Any:
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__gt__(self, other)
        return tuple(map(cmpkey, self)) > tuple(map(cmpkey, other))

    @setdoc.basic
    def __init__(
        self: Self,
        data: Optional[Iterable[Item]] = None,
        /,
        **kwargs: Any,
    ) -> None:
        self._data = ()
        if data is not None:
            self.data = data
        self._init_kwargs(**kwargs)

    @setdoc.basic
    def __le__(self: Self, other: object) -> Any:
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__le__(self, other)
        return tuple(map(cmpkey, self)) <= tuple(map(cmpkey, other))

    @setdoc.basic
    def __lt__(self: Self, other: object) -> Any:
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__lt__(self, other)
        return tuple(map(cmpkey, self)) < tuple(map(cmpkey, other))

    __ne__ = BaseDataObject.__ne__

    __repr__ = HoldList.__repr__

    @classmethod
    @abstractmethod
    def _data_parse(cls: type[Self], value: list[Any]) -> Iterable[Item]: ...

    @property
    @setdoc.basic
    def data(self: Self) -> tuple[Item, ...]:
        return self._data

    @data.setter
    def data(self: Self, value: Iterable[Any]) -> None:
        self._data = tuple(self._data_parse(list(value)))

    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        self.data = sorted(
            self,
            key=cmp_to_key(cmp) if key is None else key,
            reverse=reverse,
        )
