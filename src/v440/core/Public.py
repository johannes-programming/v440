from __future__ import annotations


from typing import *


from v440._utils.VList import VList
from v440._utils import utils

from v440.core.Release import Release
import keyalias
 


import dataclasses

import packaging.version
from catchlib import Catcher

from v440._utils import QualifierParser, utils
from v440._utils.Base import Base
from v440._utils.Pattern import Pattern
from v440.core.Local import Local
from v440.core.Pre import Pre
from v440.core.Release import Release
from v440.core.VersionError import VersionError


calc:utils.Digest = utils.Digest("calc")
@calc.overload()
def calc() -> list:
    return [0, 0]
@calc.overload(int)
def calc(value:int)->list:
    return [0, value]
@calc.overload(list)
def calc(value:list)->list:
    return value
@calc.overload(str)
def calc(value:str)->list:
    if "!" in value:
        return value.split("!")
    else:
        return [0, value]

@keyalias.keyalias(epoch=0, release=1)
class Base(VList):
    data: list
    epoch: int
    release: Release

    def __init__(self: Self, data: Any = None) -> None:
        self._data = [0, Release()]
        self.data = data

    def __str__(self: Self) -> str:
        if self.epoch:
            return "%s!%s" % tuple(self)
        else:
            return str(self.release)
        
    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        x:Any
        y:Any
        x, y = calc(value)
        if x < 0:
            raise ValueError
        self._data[0] = x
        self._data[1].data = y

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        return ans
   
QUALIFIERDICT = dict(
    dev="dev",
    post="post",
    r="post",
    rev="post",
)

public_iterparse: utils.Digest = utils.Digest("public_iterparse")

@public_iterparse.overload()
def public_iterparse() -> Generator:
    yield "base", None
    yield "pre", None
    yield "post", None
    yield "dev", None

@public_iterparse.overload(int)
def public_iterparse(value: int) -> Generator:
    yield "base", value
    yield "pre", None
    yield "post", None
    yield "dev", None

@public_iterparse.overload(str)
def public_iterparse(value:str) -> Generator:
    match: Any = Pattern.PUBLIC.leftbound.search(value)
    yield "base", value[: match.end()]
    v:str = value[match.end() :]
    yield "pre", None
    yield "post", None
    yield "dev", None
    m: Any
    n: Any
    x: Any
    y: Any
    while v:
        m = Pattern.QUALIFIERS.leftbound.search(v)
        v = v[m.end() :]
        if m.group("N"):
            yield "post", m.group("N")
        else:
            x = m.group("l")
            y = m.group("n")
            n = QUALIFIERDICT.get(x, "pre")
            yield n, (x, y)

@dataclasses.dataclass(order=True)
class _Version:
    epoch: int = 0
    release: Release = dataclasses.field(default_factory=Release)
    pre: Pre = dataclasses.field(default_factory=Pre)
    post: Optional[int] = None
    dev: Optional[int] = None
    local: Local = dataclasses.field(default_factory=Local)

    def copy(self: Self) -> Self:
        return dataclasses.replace(self)

    def todict(self: Self) -> dict:
        return dataclasses.asdict(self)


class Version(Base):
    base: Self
    dev: Optional[int]
    epoch: int
    local: Local
    post: Optional[int]
    pre: Pre
    public: Self
    release: Release
    string: str

    def __bool__(self: Self) -> bool:
        return self._data != _Version()

    def __init__(self: Self, string: Any = "0", /, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", _Version())
        self.string = string
        self.update(**kwargs)

    def __le__(self: Self, other: Any) -> bool:
        return self._cmpkey() <= type(self)(other)._cmpkey()

    def __setattr__(self: Self, name: str, value: Any) -> None:
        a: dict = dict()
        b: dict = dict()
        catcher: Catcher = Catcher()
        x: Any
        y: Any
        for x, y in self._data.todict().items():
            with catcher.catch(AttributeError):
                a[x] = y.string
            if catcher.caught is not None:
                b[x] = y
        try:
            Base.__setattr__(self, name, value)
        except VersionError:
            for x, y in a.items():
                getattr(self._data, x).data = y
            for x, y in b.items():
                setattr(self._data, x, y)
            raise

    def __str__(self: Self) -> str:
        return self.string

    _calc_base: utils.Digest = utils.Digest("base")

    @_calc_base.overload()
    def _calc_base(self: Self) -> None:
        return None, None

    @_calc_base.overload(int)
    def _calc_base(self: Self, value: int) -> None:
        return None, value

    @_calc_base.overload(str)
    def _calc_base(self: Self, value: str) -> None:
        if "!" in value:
            return value.split("!", 1)
        else:
            return 0, value

    _calc_epoch: utils.Digest = utils.Digest("_calc_epoch")

    @_calc_epoch.overload()
    def _calc_epoch(self: Self) -> None:
        return 0

    @_calc_epoch.overload(int)
    def _calc_epoch(self: Self, value: int) -> None:
        if value < 0:
            raise ValueError
        return value

    @_calc_epoch.overload(str)
    def _calc_epoch(self: Self, value: str) -> None:
        v: Any = Pattern.EPOCH.bound.search(value)
        v = v.group("n")
        if v is None:
            return 0
        else:
            return int(v)

    _calc_string: utils.Digest = utils.Digest("_calc_string")

    @_calc_string.overload()
    def _calc_string(self: Self) -> tuple:
        return None, None

    @_calc_string.overload(int)
    def _calc_string(self: Self, value: int) -> tuple:
        return value, None

    @_calc_string.overload(str)
    def _calc_string(self: Self, value: str) -> list | tuple:
        if "+" in value:
            return value.split("+", 1)
        else:
            return value, None

    def _cmpkey(self: Self) -> tuple:
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
    def base(self: Self) -> Self:
        ans: Self = self.public
        ans.dev = None
        ans.pre = None
        ans.post = None
        return ans

    @base.setter
    def base(self: Self, value: Any) -> None:
        self.epoch, self.release = self._calc_base(value)

    def clear(self: Self) -> None:
        self.string = None

    def copy(self: Self) -> Self:
        return type(self)(self)

    @property
    def dev(self: Self) -> Optional[int]:
        return self._data.dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self._data.dev = QualifierParser.DEV(value)

    @property
    def epoch(self: Self) -> int:
        return self._data.epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        self._data.epoch = self._calc_epoch(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
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

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isprerelease(self: Self) -> bool:
        return self.isdevrelease() or not self.pre.isempty()

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def local(self: Self) -> Local:
        return self._data.local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self._data.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def post(self: Self) -> Optional[int]:
        return self._data.post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self._data.post = QualifierParser.POST(value)

    @property
    def pre(self: Self) -> Pre:
        return self._data.pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self._data.pre.data = value

    @property
    def public(self: Self) -> Self:
        ans: Self = self.copy()
        ans.local = None
        return ans
    
    @public.setter
    def public(self:Self, value:Any)->None:
        x:Any
        y:Any
        for x, y in public_iterparse(value):
            setattr(self, x, y)

    @property
    def release(self: Self) -> Release:
        return self._data.release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self._data.release.data = value

    @property
    def string(self: Self) -> str:
        return self.format()
    @string.setter
    def string(self:Self, value:Any) -> None:
        self.public, self.local = self._calc_string(value)

    def update(self: Self, **kwargs: Any) -> None:
        a: Any
        m: str
        x: Any
        y: Any
        for x, y in kwargs.items():
            a = getattr(type(self), x)
            if isinstance(a, property):
                setattr(self, x, y)
                continue
            m: str = "%r is not a property"
            m %= x
            raise AttributeError(m)

    # legacy
    data: str
    data = string