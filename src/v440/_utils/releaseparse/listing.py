from __future__ import annotations

import string
from typing import *

from overloadable import Overloadable

from v440._utils.releaseparse.numerals import numeral

__all__ = ["tolist"]


@Overloadable
def tolist(value: Any, *, slicing: Any) -> list:
    if value is None:
        return
    if isinstance(value, int):
        return int
    if hasattr(value, "__iter__") and not isinstance(value, str):
        return list
    return str


@tolist.overload()
def tolist(value: None, *, slicing: Any) -> list:
    return list()


@tolist.overload(int)
def tolist(value: int, *, slicing: Any) -> list:
    v: int = int(value)
    if value < 0:
        raise ValueError
    return [v]


@tolist.overload(list)
def tolist(value: int, *, slicing: Any) -> list:
    return list(map(numeral, value))


@tolist.overload(str)
def tolist(value: Any, *, slicing: Any) -> list:
    s: Any
    if isinstance(value, str):
        s = slicing
    else:
        s = "never"
    v: str = str(value)
    if v == "":
        return list()
    if "" == v.strip(string.digits) and s in (len(v), "always"):
        return list(map(int, v))
    v = v.lower().strip()
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    if v.startswith("v") or v.startswith("."):
        v = v[1:]
    l: list = v.split(".")
    if "" in l:
        raise ValueError
    l = list(map(numeral, l))
    return l
