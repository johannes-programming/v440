from __future__ import annotations

import operator
from typing import *

__all__ = ["torange"]


def torange(key: slice, length: int) -> range:
    step: int = calcstep(key.step)
    start: int = calcstart(key.start, length=length, fwd=step > 0)
    stop: int = calcstop(key.stop, length=length, fwd=step > 0)
    ans: range = range(start, stop, step)
    return ans


def calcstep(value: Optional[SupportsIndex]) -> int:
    if value is None:
        return 1
    return operator.index(value)


def calcstart(value: Optional[SupportsIndex], *, length: int, fwd: bool) -> int:
    ans: int
    if value is None:
        ans = 0 if fwd else (length - 1)
    else:
        ans = operator.index(value)
    if ans < 0:
        ans += length
    if ans < 0:
        ans = 0 if fwd else -1
    return ans


def calcstop(value: Optional[SupportsIndex], *, length: int, fwd: bool) -> int:
    ans: int
    if value is None:
        ans = length if fwd else -1
    else:
        ans = operator.index(value)
    if ans < 0:
        ans += length
    if ans < 0:
        ans = 0 if fwd else -1
    return ans
