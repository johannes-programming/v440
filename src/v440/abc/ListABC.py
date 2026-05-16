from abc import abstractmethod
from typing import *

import cmp3
import setdoc
from datahold import BaseDataObject, HoldList
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC

__all__ = ["ListABC"]

Item = TypeVar("Item")


class ListABC(CoreABC, HoldList[Item]):

    __slots__ = ()

    @setdoc.basic
    def __add__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = self.data + alt
        return ans

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    __eq__ = BaseDataObject.__eq__

    @setdoc.basic
    def __ge__(self: Self, other: object) -> Any:
        exc: Exception
        x: Any
        y: Any
        z: int
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__ge__(self, other)
        try:
            return BaseDataObject.__ge__(self, other)
        except Exception as exc_:
            exc = exc_
        for x, y in zip(self, other):
            if x is y or x == y:
                continue
            z = bool(isinstance(x, int)) - bool(isinstance(y, int))
            if z == -1:
                return False
            if z == 1:
                return True
            raise exc
        return len(self) >= len(other)

    @setdoc.basic
    def __gt__(self: Self, other: object) -> Any:
        exc: Exception
        x: Any
        y: Any
        z: int
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__gt__(self, other)
        try:
            return BaseDataObject.__gt__(self, other)
        except Exception as exc_:
            exc = exc_
        for x, y in zip(self, other):
            if x is y or x == y:
                continue
            z = bool(isinstance(x, int)) - bool(isinstance(y, int))
            if z == -1:
                return False
            if z == 1:
                return True
            raise exc
        return len(self) > len(other)

    @setdoc.basic
    def __le__(self: Self, other: object) -> Any:
        exc: Exception
        x: Any
        y: Any
        z: int
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__le__(self, other)
        try:
            return BaseDataObject.__le__(self, other)
        except Exception as exc_:
            exc = exc_
        for x, y in zip(self, other):
            if x is y or x == y:
                continue
            z = bool(isinstance(x, int)) - bool(isinstance(y, int))
            if z == -1:
                return True
            if z == 1:
                return False
            raise exc
        return len(self) <= len(other)

    @setdoc.basic
    def __lt__(self: Self, other: object) -> Any:
        exc: Exception
        x: Any
        y: Any
        z: int
        if not isinstance(other, BaseDataObject):
            return NotImplemented
        if not isinstance(other, ListABC):
            return BaseDataObject.__lt__(self, other)
        try:
            return BaseDataObject.__lt__(self, other)
        except Exception as exc_:
            exc = exc_
        for x, y in zip(self, other):
            if x is y or x == y:
                continue
            z = bool(isinstance(x, int)) - bool(isinstance(y, int))
            if z == -1:
                return True
            if z == 1:
                return False
            raise exc
        return len(self) < len(other)

    @setdoc.basic
    def __mul__(self: Self, other: Any) -> Self:
        ans: Self
        ans = type(self)()
        ans.data = self.data * other
        return ans

    __ne__ = BaseDataObject.__ne__

    @setdoc.basic
    def __radd__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = alt + self.data
        return ans

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, list(self))

    @setdoc.basic
    def __rmul__(self: Self, other: SupportsIndex) -> Self:
        return self * other

    def _cmp(self: Self) -> tuple:
        return tuple(map(self._sort, self.data))

    @classmethod
    @abstractmethod
    def _data_parse(cls: type[Self], value: list) -> Iterable[Item]: ...

    @classmethod
    @abstractmethod
    def _sort(cls: type[Self], value: Any) -> Any: ...

    @property
    @setdoc.basic
    def data(self: Self) -> tuple[Item, ...]:
        return self._data

    @data.setter
    def data(self: Self, value: Iterable) -> None:
        self._data = tuple(self._data_parse(list(value)))
