from __future__ import annotations

import functools
from typing import *


from v440._utils import utils
from v440._utils.VList import VList
from overloadable import overloadable

__all__ = ["Local"]

class Local(VList):

    def __add__(self, other, /):
        other = self._tolist(other)
        ans = self.copy()
        ans.data = ans.data + other
        return ans
        

    def __le__(self, other: Iterable) -> bool:
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return self._cmpkey() <= other._cmpkey()
        return self.data <= other
    
    def __radd__(self, other, /):
        other = self._tolist(other)
        ans = self.copy()
        ans.data = other + ans.data
        return ans
    
    @overloadable
    def __setitem__(self, key, value:Any):
        return type(key) is slice
    @__setitem__.overload(False)
    def __setitem__(self, key:SupportsIndex, value:Any)->None:
        data = self.data
        data[key] = value
        self.data = data
    @__setitem__.overload(True)
    def __setitem__(self, key:slice, value:Any)->None:
        start, stop, step = key.indices(len(self))
        if step != 1:
            length = "none"
        else:
            length = stop - start
        value = self._tolist(value, length)
        data = self.data
        data[start:stop:step] = value
        self.data = data


    def __str__(self) -> str:
        return ".".join(str(x) for x in self)

    def _cmpkey(self) -> list:
        return [self._sortkey(x) for x in self]

    @staticmethod
    def _sortkey(value) -> Tuple[bool, Any]:
        return type(value) is int, value
    
    @classmethod
    def _tolist(cls, value, length="none"):
        if value is None:
            return list()
        if isinstance(value, int):
            return [int(value)]
        if isinstance(value, str):
            pass
        elif hasattr(value, "__iter__"):
            return list(value)
        else:
            length = "none"
        value = str(value).lower().strip()
        if length in (len(value), "any"):
            return list(value)
        if value.startswith("+"):
            value = value[1:]
        value = value.split(".")
        value = [utils.segment(x) for x in value]
        return value

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
