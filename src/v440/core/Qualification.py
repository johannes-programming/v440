from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Pattern import Pattern
from v440._utils.VList import VList
from v440.core.Pre import Pre

__all__ = ["Qualification"]

parse_data: utils.Digest = utils.Digest()


@parse_data.overload()
def parse_data() -> tuple:
    return None, None, None


@parse_data.overload(int)
def parse_data(value: int) -> tuple:
    return None, value, None


@parse_data.overload(list)
def parse_data(value: list) -> tuple:
    return tuple(value)


@parse_data.overload(str)
def parse_data(value: str) -> tuple:
    v: str = value
    pre = None
    post = None
    dev = None
    m: Any
    x: Any
    y: Any
    while v:
        m = Pattern.QUALIFIERS.leftbound.search(v)
        v = v[m.end() :]
        if m.group("N"):
            post = m.group("N")
            continue
        x = m.group("l")
        y = m.group("n")
        if x == "dev":
            dev = y
            continue
        if x in ("post", "r", "rev"):
            post = y
            continue
        pre = (x, y)
    return pre, post, dev


parse_optnum: utils.Digest = utils.Digest()


@parse_optnum.overload()
def parse_optnum() -> None:
    return


@parse_optnum.overload(int)
def parse_optnum(value: int):
    return utils.numeral(value)


@parse_optnum.overload(str)
def parse_optnum(value: str):
    return utils.numeral(value)


class Qualification(VList):

    __slots__ = ("_pre", "_post", "_dev")
    data: list
    pre: Pre
    post: Optional[int]
    dev: Optional[int]

    def __init__(self: Self, data: Any = None) -> None:
        self._pre = Pre()
        self._post = None
        self._dev = None
        self.data = data

    def __le__(self: Self, other: Any) -> bool:
        return self._cmpkey() <= type(self)(other)._cmpkey()

    def __str__(self: Self) -> str:
        ans: str = ""
        ans += str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    def _cmpkey(self: Self) -> tuple:
        ans: list = self.data
        if not ans[0].isempty():
            ans[0] = tuple(ans.pre)
        elif ans[1] is not None:
            ans[0] = "z", float("inf")
        elif ans[2] is None:
            ans[0] = "z", float("inf")
        else:
            ans[0] = "", -1
        if ans[1] is None:
            ans[1] = -1
        if ans[2] is None:
            ans[2] = float("inf")
        return ans

    @property
    def data(self: Self) -> list:
        return [self.pre, self.post, self.dev]

    @data.setter
    @utils.vGuard
    def data(self: Self, value: Any) -> None:
        self.pre, self.post, self.dev = parse_data(value)

    @property
    def dev(self: Self) -> Pre:
        return self._dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self._dev = parse_optnum(value)

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isprerelease(self: Self) -> bool:
        return self.isdevrelease() or not self.pre.isempty()

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def pre(self: Self) -> Pre:
        return self._pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self.pre.data = value

    @property
    def post(self: Self) -> Pre:
        return self._post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self._post = parse_optnum(value)
