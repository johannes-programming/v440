from __future__ import annotations

import functools
from typing import *

import setdoc

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.utils import guard
from v440._utils.VList import VList

__all__ = ["Local"]


class Local(VList):
    __slots__ = ()

    data: list[int | str]

    @setdoc.basic
    def __init__(self: Any, data: Any = None) -> None:
        self._data = list()
        self.data = data

    @setdoc.basic
    def __le__(self: Self, other: Iterable) -> bool:
        ans: bool
        try:
            alt: Self = type(self)(other)
        except ValueError:
            ans = self.data <= other
        else:
            ans = self._cmp() <= alt._cmp()
        return ans

    @setdoc.basic
    def __str__(self: Self) -> str:
        return ".".join(map(str, self))

    def _cmp(self: Self) -> list:
        return list(map(self._sortkey, self))

    _data_calc: Digest = Digest("_data_calc")

    @_data_calc.overload()
    def _data_calc(self: Self) -> list:
        return list()

    @_data_calc.overload(int)
    def _data_calc(self: Self, value: int) -> list:
        return [value]

    @_data_calc.overload(list)
    def _data_calc(self: Self, value: list) -> list:
        ans: list = list(map(utils.segment, value))
        if None in ans:
            raise ValueError
        return ans

    @_data_calc.overload(str)
    def _data_calc(self: Self, value: str) -> list:
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        ans: list = v.split(".")
        ans = list(map(utils.segment, ans))
        if None in ans:
            raise ValueError
        return ans

    @staticmethod
    def _sortkey(value: Any) -> tuple[bool, Any]:
        return type(value) is int, value

    @property
    @setdoc.basic
    def data(self: Self) -> list[int | str]:
        return list(self._data)

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self._data = self._data_calc(value)

    @functools.wraps(VList.sort)
    def sort(self: Self, /, *, key: Any = None, **kwargs: Any) -> None:
        k: Any = self._sortkey if key is None else key
        self._data.sort(key=k, **kwargs)
