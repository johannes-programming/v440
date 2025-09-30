from __future__ import annotations

import string
from typing import *

from v440._utils.Digest import Digest
from v440.core.VersionError import VersionError


def numeral(value: Any, /) -> int:
    v: int
    try:
        v = _segment(value)
    except Exception:
        e: str = "%r is not a valid numeral segment"
        raise VersionError(e % value) from None
    return v


def _segment(value: Any, /) -> int:
    if isinstance(value, int):
        return int(value)
    s: str = str(value)
    if s == "":
        return 0
    i: int = int(s)
    if i < 0:
        raise ValueError
    return i
