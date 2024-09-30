from __future__ import annotations

import functools
import string
from typing import *

SEGCHARS = string.ascii_lowercase + string.digits


def digest(old, /):
    byNone = getattr(old, "byNone", None)
    byInt = getattr(old, "byInt", None)
    byList = getattr(old, "byList", None)
    byStr = getattr(old, "byStr", None)

    def new(*args, **kwargs):
        args = list(args)
        value = args.pop()
        if value is None:
            return byNone(*args, **kwargs)
        if isinstance(value, int):
            value = int(value)
            return byInt(*args, value, **kwargs)
        if isinstance(value, str) or not hasattr(value, "__iter__"):
            value = str(value).lower().strip()
            return byStr(*args, value, **kwargs)
        else:
            value = list(value)
            return byList(*args, value, **kwargs)

    new.__name__ = old.__name__
    return new


def literal(value, /):
    value = segment(value)
    if type(value) is str:
        return value
    e = "%r is not a valid literal segment"
    e = VersionError(e % value)
    raise e


def numeral(value, /):
    value = segment(value)
    if type(value) is int:
        return value
    e = "%r is not a valid numeral segment"
    e = VersionError(e % value)
    raise e


def segment(value, /):
    try:
        return _segment(value)
    except:
        e = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


@digest
class _segment:
    def byNone():
        return

    def byInt(value, /):
        if value < 0:
            raise ValueError
        return value

    def byStr(value, /):
        if value.strip(SEGCHARS):
            raise ValueError(value)
        if value.strip(string.digits):
            return value
        if value == "":
            return 0
        return int(value)


def toindex(value, /):
    ans = value.__index__()
    if type(ans) is not int:
        e = "__index__ returned non-int (type %s)"
        e %= type(ans).__name__
        raise TypeError(e)
    return ans


def torange(key, length):
    start = key.start
    stop = key.stop
    step = key.step
    if step is None:
        step = 1
    else:
        step = toindex(step)
        if step == 0:
            raise ValueError
    fwd = step > 0
    if start is None:
        start = 0 if fwd else (length - 1)
    else:
        start = toindex(start)
    if stop is None:
        stop = length if fwd else -1
    else:
        stop = toindex(stop)
    if start < 0:
        start += length
    if start < 0:
        start = 0 if fwd else -1
    if stop < 0:
        stop += length
    if stop < 0:
        stop = 0 if fwd else -1
    return range(start, stop, step)


class Base:

    def __ge__(self, other, /):
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return other <= self
        return self.data >= other

    def __le__(self, other, /):
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return self._data <= other._data
        return self.data <= other

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        cls = type(self)
        attr = getattr(cls, name)
        if type(attr) is not property:
            e = "%r is not a property"
            e %= name
            e = AttributeError(e)
            raise e
        try:
            object.__setattr__(self, name, value)
        except VersionError:
            raise
        except:
            e = "%r is an invalid value for %r"
            e %= (value, cls.__name__ + "." + name)
            raise VersionError(e)


class VersionError(ValueError): ...
