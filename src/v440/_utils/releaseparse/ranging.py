from __future__ import annotations

import operator
from typing import *

__all__ = ["torange"]


def torange(key: Any, length: Any) -> range:
    start: Any = key.start
    stop: Any = key.stop
    step: Any = key.step
    if step is None:
        step = 1
    else:
        step = operator.index(step)
        if step == 0:
            raise ValueError
    fwd: bool = step > 0
    if start is None:
        start = 0 if fwd else (length - 1)
    else:
        start = operator.index(start)
    if stop is None:
        stop = length if fwd else -1
    else:
        stop = operator.index(stop)
    if start < 0:
        start += length
    if start < 0:
        start = 0 if fwd else -1
    if stop < 0:
        stop += length
    if stop < 0:
        stop = 0 if fwd else -1
    ans: range = range(start, stop, step)
    return ans
