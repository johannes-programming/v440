from __future__ import annotations

import dataclasses
import string
import typing

import packaging.version
from overloadable import overloadable
from protectedclasses import Protected
from scaevola import Scaevola

from v440._core import Parser, utils
from v440._core.Local import Local
from v440._core.Pattern import Pattern
from v440._core.Pre import Pre
from v440._core.Release import Release


@dataclasses.dataclass(order=True)
class _Version:
    epoch: int = 0
    release: Release = dataclasses.field(default_factory=Release)
    pre: Pre = dataclasses.field(default_factory=Pre)
    post: typing.Optional[int] = None
    dev: typing.Optional[int] = None
    local: Local = dataclasses.field(default_factory=Local)

    def copy(self):
        return dataclasses.replace(self)


class Version(Protected, Scaevola):
    def __bool__(self):
        return self._data != _Version()

    def __eq__(self, other) -> bool:
        try:
            other = type(self)(other)
        except utils.VersionError:
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        raise TypeError("unhashable type: %r" % type(self).__name__)

    def __init__(self, data="0", /, **kwargs) -> None:
        self._data = _Version()
        self.data = data
        self.update(**kwargs)

    def __le__(self, other) -> bool:
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __lt__(self, other) -> bool:
        return (self != other) and (self <= other)

    __repr__ = utils.Base.__repr__

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

    @staticmethod
    def _qualifiername(value, /):
        if value == "dev":
            return "dev"
        if value in ("post", "rev", "r"):
            return "post"
        return "pre"

    def _qualifiersetter1(self, value, /):
        k = value.rstrip(string.digits)
        n = self._qualifiername(k)
        setattr(self, n, value)

    def _qualifiersetter2(self, x, y, /):
        n = self._qualifiername(x)
        setattr(self, n, (x, y))

    @overloadable
    def _qualifierssetter(self, value, /):
        self.pre = None
        self.post = None
        self.dev = None
        if value is None:
            return "del"
        if utils.isiterable(value):
            return "list"
        return "str"

    @_qualifierssetter.overload("del")
    def _qualifierssetter(self, value, /): ...

    @_qualifierssetter.overload("list")
    def _qualifierssetter(self, value, /):
        value = [utils.segment(x) for x in value]
        while value:
            x = value.pop(0)
            if type(x) is not str:
                self.post = x
            elif not value:
                self._qualifiersetter1(x)
            elif type(value[0]) is str:
                self._qualifiersetter1(x)
            elif set(string.digits) & set(x):
                self._qualifiersetter1(x)
            else:
                y = value.pop(0)
                self._qualifiersetter2(x, y)

    @_qualifierssetter.overload("str")
    def _qualifierssetter(self, value, /):
        value = str(value).lower().strip()
        while value:
            m = Pattern.QUALIFIERS.leftbound.search(value)
            value = value[m.end() :]
            if m.group("N"):
                self.post = m.group("N")
            else:
                l = m.group("l")
                n = m.group("n")
                self._qualifiersetter2(l, n)

    @property
    def base(self) -> str:
        if self.epoch:
            return "%s!%s" % (self.epoch, self.release)
        else:
            return str(self.release)

    @base.setter
    @utils.setterbackupdeco
    def base(self, v):
        if v is None:
            del self.epoch
            del self.release
            return
        v = str(v)
        if "!" in v:
            self.epoch, self.release = v.split("!", 2)
        else:
            self.epoch, self.release = 0, v

    @base.deleter
    def base(self):
        self.base = None

    def clear(self):
        self.data = None

    def copy(self):
        return type(self)(self)

    @property
    def data(self):
        return self.format()

    @data.setter
    @utils.setterbackupdeco
    def data(self, x):
        x = str(x)
        if "+" in x:
            self.public, self.local = x.split("+", 2)
        else:
            self.public, self.local = x, None

    @data.deleter
    def data(self):
        del self.public
        del self.local

    @property
    def dev(self):
        return self._data.dev

    @dev.setter
    @utils.setterbackupdeco
    def dev(self, value):
        self._data.dev = Parser.DEV.parse(value)

    @dev.deleter
    def dev(self):
        self.dev = None

    @property
    def epoch(self):
        return self._data.epoch

    @epoch.setter
    @utils.setterbackupdeco
    def epoch(self, v):
        if v is None:
            self._data.epoch = 0
            return
        if isinstance(v, int):
            v = int(v)
            if v < 0:
                raise ValueError
            self._data.epoch = v
            return
        v = str(v).lower().strip()
        v = Pattern.EPOCH.bound.fullmatch(v).group("n")
        if v is None:
            self._data.epoch = 0
            return
        self._data.epoch = int(v)

    @epoch.deleter
    def epoch(self):
        self.epoch = None

    def format(self, cutoff=None) -> str:
        ans = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        ans += self.qualifiers
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
    @utils.setterbackupdeco
    def local(self, value):
        self._data.local = Local(value)

    @local.deleter
    def local(self):
        self.local = None

    def packaging(self):
        return packaging.version.Version(self.data)

    @property
    def post(self):
        return self._data.post

    @post.setter
    @utils.setterbackupdeco
    def post(self, value):
        self._data.post = Parser.POST.parse(value)

    @post.deleter
    def post(self):
        self.post = None

    @property
    def pre(self):
        return self._data.pre

    @pre.setter
    @utils.setterbackupdeco
    def pre(self, data, /):
        self._data.pre = Pre(data)

    @pre.deleter
    def pre(self):
        self.pre = None

    @property
    def public(self) -> str:
        return self.base + self.qualifiers

    @public.setter
    @utils.setterbackupdeco
    def public(self, v):
        if v is None:
            del self.base
            del self.qualifiers
            return
        v = str(v).strip().lower()
        match = Pattern.PUBLIC.leftbound.search(v)
        self.base = v[: match.end()]
        self.qualifiers = v[match.end() :]

    @public.deleter
    def public(self):
        self.public = None

    @property
    def qualifiers(self):
        ans = str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    @qualifiers.setter
    @utils.setterbackupdeco
    def qualifiers(self, value):
        self._qualifierssetter(value)

    @qualifiers.deleter
    def qualifiers(self):
        self.qualifiers = None

    @property
    def release(self) -> Release:
        return self._data.release

    @release.setter
    @utils.setterbackupdeco
    def release(self, value):
        self._data.release = Release(value)

    @release.deleter
    def release(self):
        self._data.release = Release()

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
