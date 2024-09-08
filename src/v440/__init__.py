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


class _Setter:
    def predeco(**kwargs):
        def ans(old):
            return _Setter.deco(old, **kwargs)

        return ans

    def parse_to_input(x, /):
        if x is None:
            return None
        if issubclass(type(x), str):
            return str(x)
        if not hasattr(x, "__iter__"):
            return str(x)
        return _Setter.parse_to_list(x)

    def parse_to_item(x, /):
        if type(x) is int:
            if x < 0:
                raise ValueError
            else:
                return x
        else:
            x = _Setter.parse_to_str(x)
            if x == "":
                return x
            if x.strip(string.digits) == "":
                return int(x)
            return x

    def parse_to_list(x, /):
        return [_Setter.parse_to_item(i) for i in x]

    def parse_to_str(x, /):
        x = str(x).lower().strip()
        return x

    def deco(old, /, *, delete=True, name=None, save=True):
        @functools.wraps(old)
        def new(self, x, /) -> None:
            if name is None:
                _name = old.__name__
            else:
                _name = name
            y = _Setter.parse_to_input(x)
            try:
                if y is None and delete:
                    delattr(self, _name)
                    return
                ans = old(self, y)
            except VersionError:
                raise
            except:
                m = "%r is not a proper value for %s"
                m %= (x, _name)
                raise VersionError(m)  # from None
            if save == False:
                return
            if save == True:
                pass
            elif save == "int":
                ans = int("0" + str(ans))
            elif save == "tuple":
                ans = tuple(ans)
            else:
                raise NotImplementedError
            setattr(self, "_" + _name, ans)

        return new


def _singleton(cls):
    return cls()


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

    @_Setter.predeco(name="version", delete=False, save=False)
    def __init_setter(self, version):
        if type(version) is list:
            raise TypeError
        if version is None:
            version = "0"
        if "+" in version:
            self.public, self.local = version.split("+")
        else:
            self.public, self.local = version, None

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
        local = [(type(x) is int, x) for x in self._local]
        return self.epoch, self.release, pre, post, dev, local

    def getreleaseitem(self, index):
        if index >= len(self.release):
            return 0
        else:
            return self.release[index]

    @property
    def base_version(self) -> str:
        ans = ""
        if self.epoch != 0:
            ans += "%s!" % self.epoch
        ans += ".".join(str(x) for x in self.release)
        return ans

    @base_version.setter
    @_Setter.predeco(save=False)
    def base_version(self, v):
        if type(v) is list:
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

    def delreleaseitem(self, index):
        if index >= len(self.release):
            return
        t = list(self.release)
        while len(t) <= index:
            t.append(0)
        del t[index]
        self.release = t

    @property
    def dev(self):
        return self._dev

    @dev.setter
    @_Setter.predeco(save="int")
    def dev(self, v):
        if type(v) is list:
            raise TypeError
        if "dev" not in v:
            v = "dev" + v
        _Regex.DEV.search(v).groups()
        v = v.strip(".-_dev")
        return v

    @dev.deleter
    def dev(self):
        self._dev = None

    @property
    def epoch(self):
        return self._epoch

    @epoch.setter
    @_Setter.predeco(save="int")
    def epoch(self, v):
        if type(v) is list:
            raise TypeError
        if v.startswith("v"):
            v = v[1:]
        if v.endswith("!"):
            v = v[:-1]
        return v

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
    def local(self):
        if not self._local:
            return None
        return ".".join(str(x) for x in self._local)

    @local.setter
    @_Setter.predeco(save="tuple")
    def local(self, v):
        if type(v) is str:
            if v.startswith("+"):
                v = v[1:]
            v = v.split(".")
            v = _Setter.parse_to_list(v)
        for i in v:
            if type(i) is int:
                continue
            if i == "":
                raise ValueError
            if i.strip(string.ascii_letters + string.digits):
                raise ValueError
        return v

    @local.deleter
    def local(self):
        self._local = None

    @property
    def major(self) -> int:
        return self.getreleaseitem(0)

    @major.setter
    @_Setter.predeco()
    def major(self, value):
        self.setreleaseitem(0, value)

    @major.deleter
    def major(self):
        self.delreleaseitem(0)

    @property
    def micro(self) -> int:
        return self.getreleaseitem(2)

    @micro.setter
    def micro(self, value):
        self.setreleaseitem(2, value)

    @micro.deleter
    def micro(self):
        self.setreleaseitem(2)

    @property
    def minor(self) -> int:
        return self.getreleaseitem(1)

    @minor.setter
    def minor(self, value):
        self.setreleaseitem(1, value)

    @minor.deleter
    def minor(self):
        self.delreleaseitem(1)

    @property
    def post(self):
        return self._post

    @post.setter
    @_Setter.predeco(save="int")
    def post(self, v):
        if type(v) is list:
            raise TypeError
        if "p" not in v and "r" not in v:
            v = "post" + v
        _Regex.POST.search(v).groups()
        v = v.strip(".-_postrev")
        return v

    @post.deleter
    def post(self):
        self._post = None

    @property
    def pre(self):
        return self._pre

    @pre.setter
    @_Setter.predeco()
    def pre(self, v):
        if type(v) is str:
            v = _Regex.PRE.search(v).groups()
            v = v[1:]
            v = _Setter.parse_to_list(v)
        l = _PREDICT[l]
        if n == "":
            n = 0
        if type(n) is str:
            raise TypeError
        return (l, n)

    @pre.deleter
    def pre(self):
        self._pre = None

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
    @_Setter.predeco(save=False)
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

    @property
    def release(self):
        return self._release or (0,)

    @release.setter
    @_Setter.predeco(save="tuple")
    def release(self, v):
        if type(v) is str:
            if v.startswith("v"):
                v = v[1:]
            v = v.split(".")
            v = _Setter.parse_to_list(v)
        if any(type(x) is str for x in v):
            raise TypeError
        return v

    @release.deleter
    def release(self):
        self._release = ()

    def setreleaseitem(self, index, value):
        t = list(self.release)
        while len(t) <= index:
            t.append(0)
        t[index] = value
        self.release = t


class VersionError(ValueError): ...
