from __future__ import annotations

import operator
from functools import partial
from typing import *

from overloadable import Overloadable

from v440._utils.releaseparse import ranging


@Overloadable
def getitem(data: tuple, key: Any) -> bool:
    return type(key) is slice


@getitem.overload(False)
def getitem(data: tuple, key: Any) -> int:
    i: int = operator.index(key)
    ans: int = getitem_int(data, i)
    return ans


@getitem.overload(True)
def getitem(data: tuple, key: Any) -> list:
    r: range = ranging.torange(key, len(data))
    f: partial = partial(getitem_int, data)
    m: map = map(f, r)
    ans: list = list(m)
    return ans


def getitem_int(data: tuple[int], key: int) -> int:
    if key < len(data):
        return data[key]
    else:
        return 0
