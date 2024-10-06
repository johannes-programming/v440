from __future__ import annotations

import functools
from typing import *
from overloadable import overloadable


from v440._utils import utils
from v440._utils.VList import VList

class Local(VList):
    def __add__(self, other, /) -> Self:
        other = type(self)(other)
        ans = self.copy()
        ans._data += other._data
        return ans
    def __ge__(self, other: Any) -> bool:
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return other <= self
        return self.data >= other
    def __iadd__(self, other: Any) -> None:
        self._data = (self + other)._data
    def __le__(self, other: Iterable) -> bool:
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return self._cmpkey() <= other._cmpkey()
        return self.data <= other
    __repr__ = utils.Base.__repr__
    __setattr__ = utils.Base.__setattr__
    @overloadable
    def __setitem__(self, key:Union[SupportsIndex, slice], value:Any) -> None:
        return type(key) is slice
    @__setitem__.overload(False)
    def __setitem__(self, key, value):
        data = self.data
        data[key] = value
        self.data = data
    @__setitem__.overload(True)
    def __setitem__(self, key:slice, value:Any)->None:
        start, stop, step = key.indices(len(self))
        if step == 1:
            length = "any"
        else:
            length = len(self)
        value = self._tolist(value, length)
        self._data[start:stop:step] = value
    __str__ = utils.Base.__str__
        


    @staticmethod
    def _tolist(value, /, length):
        if value is None:
            return []
        if isinstance(value, int):
            value = int(value)
            if value < 0:
                raise ValueError
            else:
                return [value]
        if isinstance(value, str):
            pass
        elif hasattr(value, "__iter__"):
            return [utils.segment(x) for x in value]
        else:
            length = "none"
        value = str(value).lower().strip()
        if length in ["any", len(value)]:
            return [utils.segment(x) for x in value]
        if value.startswith("+"):
            value = value[1:]
        value = value.replace("_", ".")
        value = value.replace("-", ".")
        value = value.split(".")
        return [utils.segment(x) for x in value]
    
        append, clear, copy, count, extend, index, insert, pop, remove, reverse, sort

    def _cmpkey(self) -> list:
        return [self._sortkey(x) for x in self]

    @staticmethod
    def _sortkey(value) -> Tuple[bool, Any]:
        return type(value) is int, value

    @property
    def data(self) -> List[Union[int, str]]:
        return list(self._data)

    @data.setter
    @utils.digest
    class data:
        def byInt(self, value: int) -> None:
            self._data = [value]

        def byList(self, value: list) -> None:
            value = [utils.segment(x) for x in value]
            if None in value:
                raise ValueError
            self._data = value

        def byNone(self) -> None:
            self._data = list()

        def byStr(self, value: str) -> None:
            if value.startswith("+"):
                value = value[1:]
            value = value.replace("_", ".")
            value = value.replace("-", ".")
            value = value.split(".")
            value = [utils.segment(x) for x in value]
            if None in value:
                raise ValueError
            self._data = value

    @functools.wraps(VList.sort)
    def sort(self, /, *, key=None, **kwargs) -> None:
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, **kwargs)
