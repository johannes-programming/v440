from __future__ import annotations

import functools
import re
import string

import scaevola

__all__ = ["VersionError", "Version"]


_PREDICT = dict(
    alpha="a",
    a="a",
    beta="b",
    b="b",
    preview="rc",
    pre="rc",
    c="rc",
    rc="rc",
)


def _setter(old):
    @functools.wraps(old)
    def new(self, x, /) -> None:
        if x is None:
            y = None
        elif not issubclass(type(x), str) and hasattr(x, "__iter__"):
            y = list(x)
        else:
            y = str(x).strip()
        try:
            if y is not None:
                ans = old(self, y)
            elif old.__name__.startswith("_"):
                raise ValueError
            else:
                delattr(self, old.__name__)
                return
        except VersionError as e:
            raise e from None
        except:
            m = "%r is not a proper value for %s"
            m %= (x, old.__name__.lstrip("_"))
            raise VersionError(m) from None
        if not old.__name__.startswith("_"):
            setattr(self, "_" + old.__name__, ans)

    return new


def _settername(name):
    def deco(old):
        old.__name__ = name
        new = _setter(old)
        return new

    return deco


def _singleton(cls):
    return cls()


def _vstrip(s, /):
    if s.startswith("v"):
        return s[1:]
    if s.startswith("V"):
        return s[1:]
    return s


class _Pattern:
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


@_singleton
class _Regex:
    def __getattr__(self, name):
        p = getattr(_Pattern, name)
        p = r"^" + p + r"$"
        ans = re.compile(p, re.VERBOSE | re.IGNORECASE)
        setattr(self, name, ans)
        return ans


class Version(scaevola.Scaevola):
    def __eq__(self, other):
        other = type(self)(other)
        return self._cmpkey() == other._cmpkey()

    def __hash__(self):
        return self._cmpkey().__hash__()

    def __init__(self, version="0") -> None:
        self.__init_setter(version)

    @_settername("_Version")
    def __init_setter(self, s=None):
        if type(s) is not str:
            raise TypeError
        if "+" in s:
            self.public, self.local = s.split("+")
        else:
            self.public, self.local = s, None

    def __le__(self, other):
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __lt__(self, other):
        other = type(self)(other)
        return self._cmpkey() < other._cmpkey()

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self) -> str:
        return "<Version(%r)>" % str(self)

    def __str__(self) -> str:
        if self.local is None:
            return self.public
        return "%s+%s" % (self.public, self.local)

    def _cmpkey(self):
        if self.pre is not None:
            pre = self.pre
        elif self.post is None and self.dev is not None:
            pre = "", -1
        else:
            pre = "z", float("inf")
        post = -1 if self.post is None else self.post
        dev = float("inf") if self.dev is None else self.dev
        local = []
        for x in self.local.split("."):
            try:
                i = int(x), ""
            except ValueError:
                i = -1, x
            local.append(i)
        return self.epoch, self.release, pre, post, dev, local

    def _getitem(self, index):
        if type(index) is int:
            if index >= len(self.release):
                return 0
            return self.release[index]
        raise TypeError

    def _setitem(self, index, value=0):
        t = list(self.release)
        while len(t) <= index:
            t.append(0)
        t[index] = value
        self.release = t

    @property
    def base_version(self) -> str:
        ans = ""
        if self.epoch != 0:
            ans += "%s!" % self.epoch
        ans += ".".join(str(x) for x in self.release)
        return ans

    @base_version.setter
    @_settername("_base_version")
    def base_version(self, v):
        if type(v) is not str:
            raise TypeError
        if "!" in v:
            self.epoch, self.release = v.split("!")
        else:
            self.epoch, self.release = 0, v

    @base_version.deleter
    def base_version(self):
        del self.epoch
        del self.release

    def bump(self, index=-1, amount=1):
        if type(index) is not int:
            raise TypeError("index must be an integer")
        if type(amount) is not int:
            raise TypeError("amount must be an integer")
        r = list(self.release)
        r += [0] * max(0, index + 1 - len(r))
        r[index] += amount
        r = r[: index + 1]
        self.release = r

    def clear(self):
        del self.public
        del self.local

    @property
    def dev(self):
        return self._dev

    @dev.setter
    @_setter
    def dev(self, v):
        if type(v) is list:
            raise TypeError
        v = v.lower()
        if "dev" not in v:
            v = "dev" + v
        _Regex.DEV.search(v).groups()
        v = v.strip(".-_dev")
        v = int("0" + v)
        return v

    @dev.deleter
    def dev(self):
        self._dev = None

    @property
    def epoch(self):
        return self._epoch

    @epoch.setter
    @_setter
    def epoch(self, v):
        if type(v) is not str:
            raise TypeError
        v = _vstrip(v)
        if v.endswith("!"):
            v = v[:-1]
        return int("0" + v)

    @epoch.deleter
    def epoch(self):
        self._epoch = 0

    def is_prerelease(self) -> bool:
        return self.dev is not None or self.pre is not None

    def is_postrelease(self) -> bool:
        return self.post is not None

    def is_devrelease(self) -> bool:
        return self.dev is not None

    @property
    def major(self) -> int:
        return self._getitem(0)

    @major.setter
    @_setter
    def major(self, value):
        self._setitem(0, value)

    @major.deleter
    def major(self):
        self._setitem(0)

    @property
    def micro(self) -> int:
        return self._getitem(2)

    @micro.setter
    @_setter
    def micro(self, value):
        self._setitem(2, value)

    @micro.deleter
    def micro(self):
        self._setitem(2)

    @property
    def minor(self) -> int:
        return self._getitem(1)

    @minor.setter
    @_setter
    def minor(self, value):
        self._setitem(1, value)

    @minor.deleter
    def minor(self):
        self._setitem(1)

    @property
    def post(self):
        return self._post

    @post.setter
    @_setter
    def post(self, v):
        if type(v) is list:
            raise TypeError
        v = v.lower()
        if "p" not in v and "r" not in v:
            v = "post" + v
        _Regex.POST.search(v).groups()
        v = v.strip(".-_postrev")
        v = int("0" + v)
        return v

    @post.deleter
    def post(self):
        self._post = None

    @property
    def pre(self):
        return self._pre

    @pre.setter
    @_setter
    def pre(self, v):
        if type(v) is str:
            v = v.lower()
            l, n = _Regex.PRE.search(v).groups()[1:]
        else:
            l, n = v
            l = str(l).lower()
            n = str(n)
            if n.strip(string.digits):
                raise ValueError
        l = _PREDICT[l]
        n = int("0" + n)
        return (l, n)

    @pre.deleter
    def pre(self):
        self._pre = None

    @property
    def release(self):
        return self._release or (0,)

    @release.setter
    @_setter
    def release(self, v):
        if type(v) is str:
            v = _vstrip(v).split(".")
        else:
            v = [str(x) for x in v]
        v = [int(x) for x in v]
        if any(x < 0 for x in v):
            raise ValueError
        v = tuple(v)
        return v

    @release.deleter
    def release(self):
        self._release = ()

    @property
    def local(self):
        return self._local

    @local.setter
    @_setter
    def local(self, v):
        if type(v) is str:
            if v.startswith("+"):
                v = v[1:]
            v = v.split(".")
        else:
            v = [str(x) for x in v]
        if not all(v):
            raise ValueError
        v = ".".join(x for x in v)
        if v.strip(string.ascii_letters + string.digits + "."):
            raise ValueError
        return v

    @local.deleter
    def local(self):
        self._local = None

    @property
    def public(self) -> str:
        ans = self.base_version
        if self.pre is not None:
            ans += "".join(str(x) for x in self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    @public.setter
    @_settername("_public")
    def public(self, v):
        if type(v) is not str:
            raise TypeError
        d = _Regex.PUBLIC.search(v).groupdict()
        names = "epoch release pre post dev".split()
        for n in names:
            setattr(self, n, d[n])

    @public.deleter
    def public(self):
        self.public = "0"


class VersionError(ValueError): ...
