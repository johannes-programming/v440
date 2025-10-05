from __future__ import annotations

import operator
from typing import *

from v440._utils.releaseparse import listing, ranging


def numeral(value: SupportsIndex) -> int:
    ans: int = operator.index(value)
    if ans < 0:
        raise ValueError
    else:
        return ans


def setitem(data: tuple, key: Any, value: Any) -> tuple:
    f: Callable
    k: int | range
    v: int | tuple[int]
    if type(key) is slice:
        f = setitem_range
        k = ranging.torange(key, len(data))
        v = tuple(map(numeral, value))
    else:
        f = setitem_int
        k = operator.index(key)
        v = numeral(value)
    return f(data, k, v)


def setitem_int(data: tuple, key: int, value: int) -> tuple:
    if key < len(data):
        edit: list = list(data)
        edit[key] = value
        return tuple(edit)
    if value == 0:
        return data
    data += (0,) * (key - len(data))
    data += (value,)
    return data


def setitem_range(data: tuple, key: range, value: tuple[int]) -> tuple:
    if key.step == 1:
        return setitem_range_1(data, key, value)
    else:
        return setitem_range_align(data, key, value)


def setitem_range_align(data: tuple, key: range, value: Any) -> tuple:
    key: list = list(key)
    value: list = listing.tolist(value, slicing=len(key))
    if len(key) != len(value):
        e = "attempt to assign sequence of size %s to extended slice of size %s"
        e %= (len(value), len(key))
        raise ValueError(e)
    ext: int = max(0, max(*key) + 1 - len(data))
    edit: list = list(data)
    edit += [0] * ext
    for k, v in zip(key, value):
        edit[k] = v
    return tuple(edit)


def setitem_range_1(data: tuple, key: range, value: Any) -> tuple:
    edit: list = list(data)
    ext: int = max(0, key.start - len(data))
    edit += ext * [0]
    l: list = listing.tolist(value, slicing="always")
    edit = edit[: key.start] + l + edit[key.stop :]
    return tuple(edit)
