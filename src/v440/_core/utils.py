from __future__ import annotations

import enum
import functools
import inspect
import re
import string
import typing

SEGCHARS = string.ascii_lowercase + string.digits
QPATTERN = r"^(?:\.?(?P<l>[a-z]+))?(?:\.?(?P<n>[0-9]+))?$"
QREGEX = re.compile(QPATTERN)


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


def qparse(value, /, *keys):
    return list(qparse_0(value, *keys))


def qparse_0(value, /, *keys):
    if value is None:
        return None, None
    if isinstance(value, int):
        if "" not in keys:
            raise ValueError
        value = int(value)
        if value < 0:
            raise ValueError
        return "", value
    if isiterable(value):
        l, n = value
        if l is None and n is None:
            return None, None
        l = str(l).lower().strip()
        if l not in keys:
            raise ValueError
        n = segment(n)
        if isinstance(n, str):
            raise TypeError
        return l, n
    value = str(value).lower().strip()
    value = value.replace("_", ".")
    value = value.replace("-", ".")
    l, n = QREGEX.fullmatch(value).groups()
    if l is None:
        l = ""
    if l not in keys:
        raise ValueError
    if n is None:
        n = 0
    else:
        n = int(n)
    return l, n


def segment(value, /):
    try:
        return segment_1(value)
    except:
        e = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e  # from None


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
    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __setattr__(self, name, value):
        cls = type(self)
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        if isinstance(getattr(cls, name), property):
            object.__setattr__(self, name, value)
            return
        e = "%r object has no property %r"
        e %= (cls.__name__, name)
        raise AttributeError(e)


class Pattern(enum.StrEnum):
    EPOCH = r"(?:(?P<epoch>[0-9]+)!)?"
    RELEASE = r"(?P<release>[0-9]+(?:\.[0-9]+)*)"
    PRE = r"""
        (?P<pre>                                          
            [-_\.]?
            (?:alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?:[0-9]+)?
        )?"""
    POST = r"""
        (?P<post>                                         
            (?:-(?:[0-9]+))
            |
            (?: [-_\.]? (?:post|rev|r) [-_\.]? (?:[0-9]+)? )
        )?"""
    DEV = r"""(?P<dev> [-_\.]? dev [-_\.]? (?:[0-9]+)? )?"""
    PUBLIC = f"v? {EPOCH} {RELEASE} {PRE} {POST} {DEV}"

    @functools.cached_property
    def regex(self):
        p = self.value
        p = r"^" + p + r"$"
        ans = re.compile(p, re.VERBOSE)
        return ans


class VersionError(ValueError): ...
