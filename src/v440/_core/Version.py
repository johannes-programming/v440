from __future__ import annotations

import dataclasses
from typing import *

import packaging.version
from datahold import OkayABC
from scaevola import Scaevola

from v440._core import Parser, utils
from v440._core.Local import Local
from v440._core.Pattern import Pattern
from v440._core.Pre import Pre
from v440._core.Release import Release

QUALIFIERDICT = dict(
    dev="dev",
    post="post",
    r="post",
    rev="post",
)


@dataclasses.dataclass(order=True)
class _Version:
    epoch: int = 0
    release: Release = dataclasses.field(default_factory=Release)
    pre: Pre = dataclasses.field(default_factory=Pre)
    post: Optional[int] = None
    dev: Optional[int] = None
    local: Local = dataclasses.field(default_factory=Local)

    def copy(self):
        return dataclasses.replace(self)


class Version(Scaevola):
    def __bool__(self):
        return self._data != _Version()

    def __eq__(self, other: Any) -> bool:
        try:
            other = type(self)(other)
        except utils.VersionError:
            return False
        return self._data == other._data

    __hash__ = OkayABC.__hash__

    def __init__(self, data: Any = "0", /, **kwargs) -> None:
        object.__setattr__(self, "_data", _Version())
        self.data = data
        self.update(**kwargs)

    def __le__(self, other) -> bool:
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __lt__(self, other) -> bool:
        return (self != other) and (self <= other)

    __repr__ = utils.Base.__repr__

    def __setattr__(self, name: str, value: Any) -> None:
        backup = self._data.copy()
        try:
            utils.Base.__setattr__(self, name, value)
        except utils.VersionError:
            self._data = backup
            raise

    def __str__(self) -> str:
        return self.data

    def _cmpkey(self) -> tuple:
        ans = self._data.copy()
        if not ans.pre.isempty():
            ans.pre = tuple(ans.pre)
        elif ans.post is not None:
            ans.pre = "z", float("inf")
        elif ans.dev is None:
            ans.pre = "z", float("inf")
        else:
            ans.pre = "", -1
        if ans.post is None:
            ans.post = -1
        if ans.dev is None:
            ans.dev = float("inf")
        return ans

    @utils.proprietary
    class base:
        def getter(self) -> str:
            ans = self.public
            del ans.dev
            del ans.pre
            del ans.post
            return ans

        @utils.digest
        class setter:
            def byInt(self, value):
                del self.epoch
                self.release = value

            def byNone(self):
                del self.epoch
                del self.release

            def byStr(self, value):
                if "!" in value:
                    self.epoch, self.release = value.split("!", 1)
                else:
                    self.epoch, self.release = 0, value

    def clear(self):
        del self.data

    def copy(self):
        return type(self)(self)

    @utils.proprietary
    class data:
        def getter(self):
            return self.format()

        @utils.digest
        class setter:
            def byInt(self, value):
                self.public = value
                del self.local

            def byNone(self):
                del self.public
                del self.local

            def byStr(self, value):
                if "+" in value:
                    self.public, self.local = value.split("+", 1)
                else:
                    self.public, self.local = value, None

    @utils.proprietary
    class dev:
        def getter(self):
            return self._data.dev

        def setter(self, value):
            self._data.dev = Parser.DEV.parse(value)

    @utils.proprietary
    class epoch:
        def getter(self):
            return self._data.epoch

        @utils.digest
        class setter:
            def byInt(self, value):
                if value < 0:
                    raise ValueError
                self._data.epoch = value

            def byNone(self):
                self._data.epoch = 0

            def byStr(self, v):
                v = Pattern.EPOCH.bound.search(v).group("n")
                if v is None:
                    self._data.epoch = 0
                else:
                    self._data.epoch = int(v)

    def format(self, cutoff=None) -> str:
        ans = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        ans += str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        if self.local:
            ans += "+%s" % self.local
        return ans

    def isprerelease(self) -> bool:
        return self.isdevrelease() or not self.pre.isempty()

    def ispostrelease(self) -> bool:
        return self.post is not None

    def isdevrelease(self) -> bool:
        return self.dev is not None

    @utils.proprietary
    class local:
        def getter(self) -> Local:
            return self._data.local

        def setter(self, value):
            self._data.local = Local(value)

    def packaging(self):
        return packaging.version.Version(self.data)

    @utils.proprietary
    class post:
        def getter(self):
            return self._data.post

        def setter(self, value):
            self._data.post = Parser.POST.parse(value)

    @utils.proprietary
    class pre:
        def getter(self) -> Pre:
            return self._data.pre

        def setter(self, data, /):
            self._data.pre = Pre(data)

    @utils.proprietary
    class public:
        def getter(self) -> str:
            ans = self.copy()
            del ans.local
            return ans

        @utils.digest
        class setter:
            def byInt(self, value):
                self.base = value
                del self.pre
                del self.post
                del self.dev

            def byNone(self):
                del self.base
                del self.pre
                del self.post
                del self.dev

            def byStr(self, value):
                match = Pattern.PUBLIC.leftbound.search(value)
                self.base = value[: match.end()]
                value = value[match.end() :]
                self.pre = None
                self.post = None
                self.dev = None
                while value:
                    m = Pattern.QUALIFIERS.leftbound.search(value)
                    value = value[m.end() :]
                    if m.group("N"):
                        self.post = m.group("N")
                    else:
                        x = m.group("l")
                        y = m.group("n")
                        n = QUALIFIERDICT.get(x, "pre")
                        setattr(self, n, (x, y))

    @utils.proprietary
    class release:
        def getter(self) -> Release:
            return self._data.release

        def setter(self, value):
            self._data.release = Release(value)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            attr = getattr(type(self), k)
            if isinstance(attr, property):
                setattr(self, k, v)
                continue
            e = "%r is not a property"
            e %= k
            e = AttributeError(e)
            raise e
