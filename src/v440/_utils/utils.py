from __future__ import annotations

import functools
import string
from typing import *

from v440._utils.Digest import Digest
from v440.core.VersionError import VersionError


def literal(value: Any, /) -> str:
    v: Any = segment(value)
    if type(v) is str:
        return v
    e: str = "%r is not a valid literal segment"
    e %= v
    raise VersionError(e)


def numeral(value: Any, /) -> int:
    v: Any = segment(value)
    if type(v) is int:
        return v
    e: str = "%r is not a valid numeral segment"
    e %= v
    raise VersionError(e)


def segment(value: Any, /) -> Any:
    try:
        return _segment(value)
    except:
        e: str = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


_segment: Digest = Digest("_segment")


@_segment.overload()
def _segment():
    return


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


def ishashable(value: Any) -> bool:
    try:
        hash(value)
    except Exception:
        return False
    else:
        return True


def guard(old: Any) -> Any:
    @functools.wraps(old)
    def new(self: Self, value: Any) -> None:
        backup: str = str(getattr(self, old.__name__))
        try:
            old(self, value)
        except VersionError:
            setattr(self, old.__name__, backup)
            raise
        except Exception:
            setattr(self, old.__name__, backup)
            msg: str = "%r is an invalid value for %r"
            target: str = type(self).__name__ + "." + old.__name__
            msg %= (value, target)
            raise VersionError(msg)

    return new
