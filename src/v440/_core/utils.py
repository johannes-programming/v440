from __future__ import annotations

import enum
import functools
import inspect
import re
import string
import typing

SEGCHARS = string.ascii_lowercase + string.digits


class EMPTY: ...


def compclass(innerclass):
    return functools.partial(compclass_core, innerclass)


def compclass_core(innerclass, outerclass):
    for n in dir(innerclass):
        if not (isnunder(n) or ismagic(n)):
            continue
        i = getattr(innerclass, n)
        if type(i) is type:
            continue
        if not callable(i):
            continue
        o = getattr(outerclass, n, EMPTY)
        o = compclass_outerfunc(n, o)
        if isnunder(n):
            o = functools.wraps(i)(o)
        setattr(outerclass, n, o)
    return outerclass


def compclass_outerfunc(n, gotten, /):
    if gotten is not EMPTY:
        return gotten

    def o(self, *args, **kwargs):
        f = getattr(self._data, n)
        y = f(*args, **kwargs)
        return y

    return o


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
    e = "%r is not a valid numeral segment"
    e = VersionError(e % value)
    try:
        x = segment(value)
    except:
        raise e
    if type(x) is int:
        return x
    if x == "":
        return 0
    raise e


def segment(value, /):
    e = "%r is not a valid segment"
    e = VersionError(e % value)
    try:
        x = str(value).lower().strip()
    except:
        raise e
    if x.strip(SEGCHARS):
        raise e
    try:
        return int(x)
    except:
        return x


def setterdeco(old, /):
    @functools.wraps(old)
    def new(self, value, /):
        if value is None:
            delattr(self, old.__name__)
            return
        try:
            old(self, value)
        except VersionError:
            raise
        except:
            e = "%r is an invalid value for %r"
            e %= (value, old.__name__)
            raise VersionError(e)

    return new


def todata(value, *args):
    try:
        return tolist(value, *args)
    except VersionError:
        raise
    except:
        e = "%r is an invalid value for %r"
        e %= (value, "data")
        raise VersionError(e)


def toindex(value, /):
    ans = value.__index__()
    if type(ans) is not int:
        raise TypeError("__index__ returned non-int (type %s)" % type(ans).__name__)
    return ans


def tolist(value, prefix):
    if value is None:
        return
    if not issubclass(type(value), str) and hasattr(value, "__iter__"):
        return list(value)
    value = str(value).lower()
    value = value.replace("-", ".")
    value = value.replace("_", ".")
    value = lsplit(value, prefix, "")[1]
    if value == "":
        return []
    value = value.split(".")
    return value


class Pattern(enum.StrEnum):
    EPOCH = r"(?:(?P<epoch>[0-9]+)!)?"
    RELEASE = r"(?P<release>[0-9]+(?:\.[0-9]+)*)"
    PRE = r"""
        (?P<pre>                                          
            [-_\.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?"""
    POST = r"""
        (?P<post>                                         
            (?:-(?:[0-9]+))
            |
            (?: [-_\.]? (?:post|rev|r) [-_\.]? (?:[0-9]+)? )
        )?"""
    DEV = r"""(?P<dev> [-_\.]? dev [-_\.]? (?:[0-9]+)? )?"""
    LOCAL = r"""(?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?"""
    PUBLIC = f"v? {EPOCH} {RELEASE} {PRE} {POST} {DEV}"

    @functools.cached_property
    def regex(self):
        p = self.value
        p = r"^" + p + r"$"
        ans = re.compile(p, re.VERBOSE)
        return ans


class VersionError(ValueError): ...
