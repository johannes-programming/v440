from __future__ import annotations

import typing

import packaging.version
import scaevola

from v440._core.Local import Local
from v440._core.Pre import Pre
from v440._core.Release import Release

from . import utils


class Version(scaevola.Scaevola):
    def __bool__(self):
        return self != type(self)()

    def __eq__(self, other) -> bool:
        other = type(self)(other)
        return self._cmpkey() == other._cmpkey()

    def __hash__(self) -> int:
        return hash(self._cmpkey())

    def __init__(self, data="0", /, **kwargs) -> None:
        self.data = data
        self.update(**kwargs)

    def __le__(self, other) -> bool:
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __lt__(self, other) -> bool:
        other = type(self)(other)
        return self._cmpkey() < other._cmpkey()

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

    def __str__(self) -> str:
        return self.data

    def _aux(self) -> str:
        ans = str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    def _cmpkey(self) -> tuple:
        if self.pre:
            pre = self.pre.data
        elif self.post is None and self.dev is not None:
            pre = "", -1
        else:
            pre = "z", float("inf")
        post = -1 if self.post is None else self.post
        dev = float("inf") if self.dev is None else self.dev
        return self.epoch, self.release, pre, post, dev, self.local

    @property
    def base(self) -> str:
        if self.epoch:
            return "%s!%s" % (self.epoch, self.release)
        else:
            return str(self.release)

    @base.setter
    @utils.setterdeco
    def base(self, v):
        v = str(v)
        if "!" in v:
            self.epoch, self.release = v.split("!")
        else:
            self.epoch, self.release = 0, v

    @base.deleter
    def base(self):
        del self.epoch
        del self.release

    def clear(self):
        del self.public
        del self.local

    def copy(self):
        return type(self)(self)

    @property
    def data(self):
        return self.format()

    @data.setter
    @utils.setterdeco
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
        return self._dev

    @dev.setter
    @utils.setterdeco
    def dev(self, v):
        v = utils.tolist(v, ".")
        if len(v) > 2:
            raise ValueError
        if len(v) == 0:
            del self.dev
            return
        if len(v) == 1:
            v = v[0]
            v = utils.lsplit(v, "dev", "")
        if v[0] != "dev":
            raise ValueError
        v = utils.numeral(v[1])
        self._dev = v

    @dev.deleter
    def dev(self):
        self._dev = None

    @property
    def epoch(self):
        return self._epoch

    @epoch.setter
    @utils.setterdeco
    def epoch(self, v):
        v = str(v)
        v = utils.lsplit(v, "v", "")[1]
        if v.endswith("!"):
            v = v[:-1]
        v = utils.numeral(v)
        self._epoch = v

    @epoch.deleter
    def epoch(self):
        self._epoch = 0

    def format(self, cutoff=None) -> str:
        ans = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff=cutoff)
        ans += self._aux()
        if self.local:
            ans += "+%s" % self.local
        return ans

    def is_prerelease(self) -> bool:
        return self.dev is not None or self.pre is not None

    def is_postrelease(self) -> bool:
        return self.post is not None

    def is_devrelease(self) -> bool:
        return self.dev is not None

    @property
    def local(self) -> str:
        return self._local

    @local.setter
    @utils.setterdeco
    def local(self, v):
        self._local = Local(v)

    @local.deleter
    def local(self):
        self._local = Local()

    def packaging(self):
        return packaging.version.Version(self.data)

    @property
    def post(self):
        return self._post

    @post.setter
    @utils.setterdeco
    def post(self, v):
        v = utils.tolist(v, ".")
        if len(v) > 2:
            raise ValueError
        if len(v) == 0:
            del self.post
            return
        prefices = "post", "rev", "r", ""
        if len(v) == 1:
            v = utils.lsplit(v[0], *prefices)
        elif v[0] not in prefices:
            raise ValueError
        v = utils.numeral(v[1])
        self._post = v

    @post.deleter
    def post(self):
        self._post = None

    @property
    def pre(self):
        return self._pre

    @pre.setter
    @utils.setterdeco
    def pre(self, data, /):
        self._pre = Pre(data)

    @pre.deleter
    def pre(self):
        self._pre = Pre()

    @property
    def public(self) -> str:
        return self.base + self._aux()

    @public.setter
    @utils.setterdeco
    def public(self, v):
        v = str(v).lower().strip()
        if v == "":
            del self.public
            return
        d = utils.Pattern.PUBLIC.regex.search(v).groupdict()
        names = "epoch release pre post dev".split()
        for n in names:
            setattr(self, n, d[n])

    @public.deleter
    def public(self):
        self.public = "0"

    @property
    def release(self) -> Release:
        return self._release

    @release.setter
    @utils.setterdeco
    def release(self, v):
        self._release = Release(v)

    @release.deleter
    def release(self):
        self._release = Release()

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
