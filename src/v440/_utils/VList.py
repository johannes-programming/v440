from abc import abstractmethod
from typing import *

import setdoc

from v440._utils.BaseList import BaseList

__all__ = ["VList"]


class VList(BaseList):

    __slots__ = ("_data",)
    data: tuple
    string: str

    @setdoc.basic
    def __add__(self: Self, other: Any) -> Self:
        return type(self)(self.data + tuple(other))

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> None:
        data: list = list(self.data)
        del data[key]
        self.data = data

    @setdoc.basic
    def __iadd__(self: Self, other: Any, /) -> Self:
        self.data = self.data + tuple(other)
        return self

    @setdoc.basic
    def __imul__(self: Self, other: Any, /) -> Self:
        self.data = self.data * other
        return self

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(self.data)

    @setdoc.basic
    def __mul__(self: Self, other: Any) -> Self:
        return type(self)(self.data * other)

    @setdoc.basic
    def __rmul__(self: Self, other: Any) -> Self:
        return self * other

    def _cmp(self: Self) -> tuple:
        return tuple(map(self._sort, self.data))

    @classmethod
    @abstractmethod
    def _sort(cls: type, value: Any): ...

    def append(self: Self, value: Self, /) -> None:
        "This method appends value to self."
        data: list = list(self.data)
        data.append(value)
        self.data = data

    def clear(self: Self) -> None:
        "This method clears the data."
        self.data = ()

    def extend(self: Self, value: Self, /) -> None:
        "This method extends self by value."
        data: list = list(self.data)
        data.extend(value)
        self.data = data

    def insert(
        self: Self,
        index: SupportsIndex,
        value: Any,
        /,
    ) -> None:
        "This method inserts value at index."
        data: list = list(self.data)
        data.insert(index, value)
        self.data = data

    def pop(self: Self, index: SupportsIndex = -1, /) -> Any:
        "This method pops an item."
        data: list = list(self.data)
        ans: Any = data.pop(index)
        self.data = data
        return ans

    def remove(self: Self, value: Any, /) -> None:
        "This method removes the first occurence of value."
        data: list = list(self.data)
        data.remove(value)
        self.data = data

    def reverse(self: Self) -> None:
        "This method reverses the order of the data."
        data: list = list(self.data)
        data.reverse()
        self.data = data

    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        data: list = list(self.data)
        k: Any = self._sort if key is None else key
        r: bool = bool(reverse)
        data.sort(key=k, reverse=r)
        self.data = data
