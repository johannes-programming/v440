from __future__ import annotations

from typing import *

import setdoc

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.utils import guard
from v440._utils.VList import VList

__all__ = ["Local"]

parse_data: Digest = Digest("parse_data")


@parse_data.overload()
def parse_data() -> tuple:
    return ()


@parse_data.overload(int)
def parse_data(value: int) -> list:
    return (value,)


@parse_data.overload(list)
def parse_data(value: list) -> list:
    ans: tuple = tuple(map(utils.segment, value))
    if None in ans:
        raise ValueError
    return ans


@parse_data.overload(str)
def parse_data(value: str) -> tuple:
    v: str = value
    if v.startswith("+"):
        v = v[1:]
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    ans: tuple = v.split(".")
    ans = tuple(map(utils.segment, ans))
    if None in ans:
        raise ValueError
    return ans


class Local(VList):
    __slots__ = ()

    data: tuple[int | str]
    string: str

    @setdoc.basic
    def __init__(self: Any, data: Any = None) -> None:
        self.data = data

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        return ".".join(map(str, self))

    @classmethod
    def _sort(cls: type, value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    @property
    @setdoc.basic
    def data(self: Self) -> tuple[int | str]:
        return self._data

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self._data = parse_data(value)
