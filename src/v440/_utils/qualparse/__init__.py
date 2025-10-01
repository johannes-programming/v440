from __future__ import annotations

import functools
import operator
import string
import types
from typing import *

import setdoc

from v440._utils.Cfg import Cfg
from v440._utils.Pattern import Pattern
from v440.core.VersionError import VersionError


# Digest
class Digest:
    __slots__ = ("__dict__", "lookup", "name", "kind")
    lookup: dict
    name: str
    kind: Any

    @setdoc.basic
    def __call__(self: Self, *args: Any, **kwargs: Any) -> Any:
        return self.wrapped(*args, **kwargs)

    def __get__(
        self: Self,
        *args: Any,
        **kwargs: Any,
    ) -> types.FunctionType | types.MethodType:
        "This magic method implements getting as an attribute from a class or an object."
        return self.wrapped.__get__(*args, **kwargs)

    @setdoc.basic
    def __init__(
        self: Self,
        name: str = "",
        kind: Any = None,
    ) -> None:
        self.lookup = dict()
        self.name = name
        self.kind = kind

    @classmethod
    def _getkey(cls: type, value: Any) -> Any:
        if value is None:
            return
        if isinstance(value, int):
            return int
        if isinstance(value, str):
            return str
        try:
            value.__iter__
        except AttributeError:
            return str
        else:
            return list

    def _overload(self: Self, key: Any, value: Any) -> Self:
        self.lookup[key] = value
        overload(value)
        return self

    def overload(self: Self, key: Any = None) -> functools.partial:
        return functools.partial(type(self)._overload, self, key)

    @functools.cached_property
    def wrapped(self: Self) -> Any:
        def new(*args: Any, **kwargs: Any) -> Any:
            args0: list = list(args)
            value: Any = args0.pop()
            key: Any = self._getkey(value)
            if key is int:
                args0.append(int(value))
            if key is str:
                args0.append(str(value).lower().strip())
            if key is list:
                args0.append(list(value))
            ans: Any = self.lookup[key](*args0, **kwargs)
            return ans

        new.__name__ = self.name
        if self.kind is not None:
            new = self.kind(new)
        return new


# segment
def segment(value: Any, /) -> Any:
    try:
        return _segment(value)
    except Exception:
        e: str = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


def _segment(value: Any) -> Any:
    if value is None:
        return
    if isinstance(value, int):
        x = int(value)
        if x < 0:
            raise ValueError
        return x
    value = str(value).lower().strip()
    if value.strip(string.ascii_lowercase + string.digits):
        raise ValueError
    if value.strip(string.digits):
        return value
    elif value == "":
        return 0
    else:
        return int(value)


# parse_pre
def parse_pre(value: Any) -> tuple:
    v: str = str(value).lower()
    if v == "":
        return None, None
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = Cfg.cfg.data["phases"][l]
    n = 0 if (n is None) else int(n)
    return l, n
