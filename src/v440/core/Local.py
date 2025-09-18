from __future__ import annotations

import functools
from typing import *

from v440._utils import utils
from v440._utils.VList import VList

__all__ = ["Local"]

parse_data: utils.Digest = utils.Digest("parse_data")


@parse_data.overload()
def parse_data(self: Self) -> None:
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
def parse_data(value: str) -> None:
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

    data: list[int | str]

    def __le__(self: Self, other: Iterable) -> bool:
        "This magic method implements self<=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except ValueError:
            ans = self.data <= other
        else:
            ans = self._cmpkey() <= alt._cmpkey()
        return ans

    def __str__(self: Self) -> str:
        "This magic method implements str(self)."
        return ".".join(map(str, self))

    def _cmpkey(self: Self) -> list:
        return list(map(self._sortkey, self))

    @staticmethod
    def _sortkey(value: Any) -> Tuple[bool, Any]:
        return type(value) is int, value

    @property
    def data(self: Self) -> list[int | str]:
        return list(self._data)

    @data.setter
    @utils.vGuard
    def data(self: Self, value: Any) -> None:
        self._data = parse_data(value)

    @functools.wraps(VList.sort)
    def sort(self: Self, /, *, key: Any = None, **kwargs: Any) -> None:
        k: Any = self._sortkey if key is None else key
        self._data.sort(key=k, **kwargs)
