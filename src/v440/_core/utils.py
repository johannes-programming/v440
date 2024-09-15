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


class EMPTY: ...


def ismagic(name):
    name = str(name)
    if len(name) < 5:
        return False
    if not name.startswith("__"):
        return False
    if not name.endswith("__"):
        return False
    if name.startswith("___"):
        return False
    if name.endswith("___"):
        return False
    return True


def isnunder(name):
    name = str(name)
    return not name.startswith("_")


def isinteger(value, /):
    return issubclass(type(value), int)


def isiterable(value, /):
    if isstring(value):
        return False
    return hasattr(value, "__iter__")


def isstring(value, /):
    return issubclass(type(value), str)


def literal(value, /):
    e = "%r is not a valid literal segment"
    e = VersionError(e % value)
    try:
        x = segment(value)
    except:
        raise e
    if type(x) is str:
        return x
    raise e


def lsplit(value: str, *prefices):
    for p in prefices:
        if value.startswith(p):
            return p, value[len(p) :]
    raise ValueError


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
    if isinteger(value):
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
        if l is None:
            raise ValueError
        l = str(l).lower().strip()
        if l not in keys:
            raise ValueError
        n = segment(n)
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
    if isinteger(value):
        value = int(value)
        if value < 0:
            raise ValueError
        else:
            return value
    value = str(value).lower().strip()
    if value.strip(SEGCHARS):
        raise ValueError
    if value.strip(string.digits):
        return value
    if value == "":
        return 0
    return int(value)


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


def toindex(value, /):
    ans = value.__index__()
    if type(ans) is not int:
        raise TypeError("__index__ returned non-int (type %s)" % type(ans).__name__)
    return ans


def tolist(value, prefix, apply):
    ans = tolist_0(value, prefix)
    ans = [apply(x) for x in ans]
    return ans


def tolist_0(value, prefix):
    if value is None:
        return list()
    if isiterable(value):
        return list(value)
    value = str(value).lower()
    value = value.replace("-", ".")
    value = value.replace("_", ".")
    value = lsplit(value, prefix, "")[1]
    if value == "":
        return list()
    value = value.split(".")
    return value


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
