from __future__ import annotations

import dataclasses
import re
import typing

import packaging.version
import scaevola

from v440._core.Local import Local
from v440._core.Pre import Pre
from v440._core.Release import Release

from . import utils

EPOCHPATTERN = r"^(?:(?P<n>[0-9]+)!?)?$"
EPOCHREGEX = re.compile(EPOCHPATTERN)
PUBLICPATTERN = r"^v?(?P<b>[0-9\.!]*[0-9])?(?P<q>[\.a-z][\.a-z0-9+])?$"


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


class Version(scaevola.Scaevola):
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

    __setattr__ = utils.Base.__setattr__

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

    def _qualifiers(self):
        ans = str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

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
            self.epoch, self.release = None, None
        v = str(v)
        if "!" in v:
            self.epoch, self.release = v.split("!")
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
            self.public, self.local = x.split("+")
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
    def dev(self, v):
        self._data.dev = utils.qparse(v, "dev", "")[1]

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
        v = EPOCHREGEX.fullmatch(v).group("n")
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
        ans += self._qualifiers()
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
    def local(self) -> str:
        return self._data.local

    @local.setter
    @utils.setterbackupdeco
    def local(self, v):
        self._data.local = Local(v)

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
    def post(self, v):
        v = utils.qparse(v, "post", "rev", "r", "")
        self._data.post = v[1]

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
        return self.base + self._qualifiers()

    @public.setter
    @utils.setterbackupdeco
    def public(self, v):
        if v is None:
            v = "0"
        else:
            v = str(v).strip().lower()
        d = utils.Pattern.PUBLIC.regex.fullmatch(v).groupdict()
        for i in d.items():
            setattr(self, *i)

    @public.deleter
    def public(self):
        self.public = None

    @property
    def release(self) -> Release:
        return self._data.release

    @release.setter
    @utils.setterbackupdeco
    def release(self, v):
        self._data.release = Release(v)

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
