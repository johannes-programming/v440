from __future__ import annotations

import functools
from typing import *

import setdoc

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.utils import guard
from v440._utils.VList import VList

__all__ = ["Local"]

parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> list:
    return list()


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return [value]


@parse_data.overload(list)
def parse_data(value: list) -> list:
    ans: list = list(map(utils.segment, value))
    if None in ans:
        raise ValueError
    return ans


@parse_data.overload(str)
def parse_data(value: str) -> list:
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

    def _cmp(self: Self) -> list:
        return list(map(self._sortkey, self))

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        return ".".join(map(str, self))

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
        self._data = parse_data(value)

    @functools.wraps(VList.sort)
    def sort(self: Self, /, *, key: Any = None, **kwargs: Any) -> None:
        k: Any = self._sortkey if key is None else key
        self._data.sort(key=k, **kwargs)
