from __future__ import annotations

import string
from typing import *

from v440._utils.Digest import Digest
from v440.core.VersionError import VersionError


def numeral(value: Any, /) -> int:
    v: Any
    try:
        v = _segment(value)
    except:
        e: str = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None
    if type(v) is int:
        return v
    e: str = "%r is not a valid numeral segment"
    e %= v
    raise VersionError(e)


_segment: Digest = Digest("_segment")


@_segment.overload(int)
def _segment(value: int, /) -> Any:
    if value < 0:
        raise ValueError
    return value


@_segment.overload(str)
def _segment(value: Any, /) -> int | str:
    if value.strip(string.ascii_lowercase + string.digits):
        raise ValueError(value)
    if value.strip(string.digits):
        return value
    elif value == "":
        return 0
    else:
        return int(value)
