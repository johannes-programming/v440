from __future__ import annotations

from typing import *

from v440.core.VersionError import VersionError

__all__ = ["numeral"]


def numeral(value: Any, /) -> int:
    v: int
    try:
        v = numeral_(value)
    except Exception:
        e: str = "%r is not a valid numeral segment"
        raise VersionError(e % value) from None
    return v


def numeral_(value: Any, /) -> int:
    if isinstance(value, int):
        return int(value)
    s: str = str(value)
    if s == "":
        return 0
    i: int = int(s)
    if i < 0:
        raise ValueError
    return i
