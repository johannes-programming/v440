from __future__ import annotations

import dataclasses
from typing import *

import packaging.version
from datahold import OkayABC
from scaevola import Scaevola
from contextlib import contextmanager

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
    @contextmanager
    def backup(self):
        epoch = self.epoch
        release = self.release.data
        pre = self.pre.data
        post = self.post
        dev = self.dev
        local = self.local.data
        try:
            yield
        except utils.VersionError:
            self.epoch = epoch
            self.release.data = release
            self.pre.data = pre
            self.post = post
            self.dev = dev
            self.local.data = local
    def copy(self):
        return dataclasses.replace(self)
    def todict(self):
        return dataclasses.asdict(self)


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
        with self._data.backup():
            utils.Base.__setattr__(self, name, value)

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

    @property
    def base(self):
        ans = self.public
        ans.dev = None
        ans.pre = None
        ans.post = None
        return ans

    @base.setter
    @utils.digest
    class base:
        def byInt(self, value):
            self.epoch = None
            self.release = value

        def byNone(self):
            self.epoch = None
            self.release = None

        def byStr(self, value):
            if "!" in value:
                self.epoch, self.release = value.split("!", 1)
            else:
                self.epoch, self.release = 0, value

    def clear(self):
        self.data = "0"

    def copy(self):
        return type(self)(self)

    @property
    def data(self):
        return self.format()
    
    @data.setter
    @utils.digest
    class data:
        def byInt(self, value):
            self.public = value
            self.local = None

        def byNone(self):
            self.public = 0
            self.local = None

        def byStr(self, value):
            if "+" in value:
                self.public, self.local = value.split("+", 1)
            else:
                self.public, self.local = value, None

    @property
    def dev(self):
        return self._data.dev

    @dev.setter
    def dev(self, value):
        self._data.dev = Parser.DEV.parse(value)

    @property
    def epoch(self):
        return self._data.epoch

    @epoch.setter
    @utils.digest
    class epoch:
        def byInt(self, value):
            self._data.epoch = value

        def byNone(self):
            self._data.epoch = None

        def byStr(self, v):
            v = Pattern.EPOCH.bound.search(v).group("n")
            if v is None:
                self._data.epoch = None
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

    @property
    def local(self) -> Local:
        return self._data.local

    @local.setter
    def local(self, value):
        self._data.local.data = value

    def packaging(self):
        return packaging.version.Version(self.data)

    @property
    def post(self):
        return self._data.post

    @post.setter
    def post(self, value):
        self._data.post = Parser.POST.parse(value)

    @property
    def pre(self):
        return self._data.pre
    
    @pre.setter
    def pre(self, value):
        self._data.pre.data = value

    @property
    def public(self):
        ans = self.copy()
        ans.local = []
        return ans

    @public.setter
    @utils.digest
    class setter:
        def byInt(self, value):
            self.base = value
            self.pre = None
            self.post = None
            self.dev = None

        def byNone(self):
            self.base = None
            self.pre = None
            self.post = None
            self.dev = None

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

    @property
    def release(self) -> Release:
        return self._data.release

    @release.setter
    def release(self, value):
        self._data.release.data = value

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
