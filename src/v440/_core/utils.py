from __future__ import annotations

import functools
import string
import typing

SEGCHARS = string.ascii_lowercase + string.digits

def digest(old, /):
    byNone = getattr(old, "byNone", None)
    byInt = getattr(old, "byInt", None)
    byList = getattr(old, "byList", None)
    byStr = getattr(old, "byStr", None)
    def new(self, value):
        h = hint(value)
        if h is None:
            return byNone(self)
        if h is int:
            value = int(value)
            return byInt(self, value)
        if h is str:
            value = str(value).lower().strip()
            return byStr(self, value) 
        if h is list:
            value = list(value)
            return byList(self, value)
        raise NotImplementedError
    return new


def hint(value, /):
    if value is None:
        return
    if isinstance(value, int):
        return int
    if isinstance(value, str):
        return str
    if hasattr(value, "__iter__"):
        return list
    return str
    

def isiterable(value, /):
    return hasattr(value, "__iter__") and not isinstance(value, str)


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

def proprietary(old, /):
    def deleter(self):
        old.setter(self, None)
    kwargs = dict()
    kwargs["fget"] = old.getter
    kwargs["fset"] = old.setter
    kwargs["fdel"] = deleter
    for v in kwargs.values():
        v.__name__ = old.__name__
    try:
        kwargs["doc"] = getattr(old, "__doc__")
    except AttributeError:
        pass
    ans = property(**kwargs)
    return ans

def segment(value, /):
    try:
        return segment_1(value)
    except:
        e = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


def segment_1(value, /):
    if value is None:
        return None
    if isinstance(value, int):
        value = int(value)
        if value < 0:
            raise ValueError
        else:
            return value
    value = str(value).lower().strip()
    if value.strip(SEGCHARS):
        raise ValueError(value)
    if value.strip(string.digits):
        return value
    if value == "":
        return 0
    return int(value)


def setterbackupdeco(old, /):
    @functools.wraps(old)
    def new(self, value, /):
        backup = self._data.copy()
        try:
            old(self, value)
        except VersionError:
            self._data = backup
            raise
        except:
            self._data = backup
            e = "%r is an invalid value for %r"
            e %= (value, old.__name__)
            raise VersionError(e)

    return new


def setterdeco(old, /):
    @functools.wraps(old)
    def new(self, value, /):
        try:
            old(self, value)
        except VersionError:
            raise
        except:
            e = "%r is an invalid value for %r"
            e %= (value, old.__name__)
            raise VersionError(e)

    return new


def toindex(value, /):
    ans = value.__index__()
    if type(ans) is not int:
        raise TypeError("__index__ returned non-int (type %s)" % type(ans).__name__)
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
        start = 0 if fwd else length - 1
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


class VersionError(ValueError): ...

