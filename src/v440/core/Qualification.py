from __future__ import annotations


from typing import *


from v440._utils.VList import VList
from v440._utils import utils

from v440.core.Pre import Pre


QUALIFIERDICT = dict(
    dev="dev",
    post="post",
    r="post",
    rev="post",
)

iterparse: utils.Digest = utils.Digest("iterparse")

@iterparse.overload()
def iterparse() -> Generator:
    yield "pre", None
    yield "post", None
    yield "dev", None

@iterparse.overload(int)
def iterparse(value: int) -> Generator:
    yield "pre", None
    yield "post", value
    yield "dev", None

@iterparse.overload(str)
def iterparse(value:str) -> Generator:
    v:str = value
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

def optnum(value:Any) -> Optional[int]:
    if value is None:
        return
    else:
        return utils.numeral(value)

class Base(VList):
    __slots__ = ("_pre", "_post", "_dev")
    pre: Pre
    post: Optional[int]
    dev: Optional[int]
    
    def __init__(self: Self, data: Any = None) -> None:
        self._data = [Pre(), None, None]
        self.data = data

    def __str__(self: Self) -> str:
        ans:str = str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans
        
    @property
    def data(self: Self) -> list:
        return [self._pre, self._post, self._dev]

    @data.setter
    def data(self: Self, value: Any) -> None:
        x:Any
        y:Any
        for x,y in iterparse(value):
            setattr(x, y)
    
    @property
    def pre(self:Self)->Pre:
        return self._pre
    @pre.setter
    def pre(self:Self, value:Any)->None:
        self._pre.data = value

    @property
    def post(self:Self)->Pre:
        return self._post
    @post.setter
    def post(self:Self, value:Any)->None:
        self._post.data = optnum(value)

    @property
    def dev(self:Self)->Pre:
        return self._dev
    @dev.setter
    def dev(self:Self, value:Any)->None:
        self._dev.data = optnum(value)