from __future__ import annotations

import operator
from typing import *

from v440.core.VersionError import VersionError

__all__ = ["numeral"]


def numeral(value: Any, /) -> int:
    v: int
    try:
        if isinstance(value, int):
            v = operator.index(value)
        else:
            v = int(str(value))
        if v < 0:
            raise ValueError
    except Exception:
        e: str = "%r is not a valid numeral segment"
        raise VersionError(e % value) from None
    return v
