from __future__ import annotations

from typing import *

from v440._utils import SimpleQualifierParser, utils
from v440._utils.BaseList import BaseList
from v440._utils.Cfg import Cfg
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.SlotList import SlotList
from v440._utils.utils import guard

__all__ = ["Qualification"]


parse_leg: Digest = Digest("parse_leg")


@parse_leg.overload()
def parse_leg() -> list:
    return [[None, None], None, None]


@parse_leg.overload(int)
def parse_leg(value: int) -> list:
    return [[None, None], abs(value), None]


@parse_leg.overload(list)
def parse_leg(value: list) -> list:
    return [value[:2]] + value[2:]


@parse_leg.overload(str)
def parse_leg(value: str) -> list:
    v = value
    prephase: Any = None
    presubphase: Any = None
    post: Any = None
    dev: Any = None
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
        prephase = x
        presubphase = y
    return [[prephase, presubphase], post, dev]


parse_pre: Digest = Digest("parse_pre")


@parse_pre.overload()
def parse_pre() -> list:
    return [None, None]


@parse_pre.overload(list)
def parse_pre(value: list) -> Any:
    l: Any
    n: Any
    l, n = list(map(utils.segment, value))
    if [l, n] == [None, None]:
        return [None, None]
    l = Cfg.cfg.data["phases"][l]
    if not isinstance(n, int):
        raise TypeError
    return [l, n]


@parse_pre.overload(str)
def parse_pre(value: str) -> list:
    if value == "":
        return [None, None]
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = Cfg.cfg.data["phases"][l]
    n = 0 if (n is None) else int(n)
    return [l, n]


class Qualification(SlotList):

    __slots__ = ("_prephase", "_presubphase", "_post", "_dev")

    data: list
    prephase: Optional[str]
    presubphase: Optional[int]
    post: Optional[int]
    dev: Optional[int]

    def __init__(self: Self, data: Any = None) -> None:
        self._prephase = None
        self._presubphase = None
        self._post = None
        self._dev = None
        self.data = data

    def __str__(self: Self) -> str:
        ans: str = ""
        if self.prephase is not None:
            ans += self.prephase
        if self.presubphase is not None:
            ans += str(self.presubphase)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        return ans

    def _cmp(self: Self) -> list:
        ans: list = list()
        if not self.pre.isempty():
            ans += list(self.pre)
        elif self.post is not None:
            ans += ["z", float("inf")]
        elif self.dev is None:
            ans += ["z", float("inf")]
        else:
            ans += ["", -1]
        ans.append(-1 if self.post is None else self.post)
        ans.append(float("inf") if self.dev is None else self.dev)
        return ans

    @property
    def data(self: Self) -> list:
        return self.pre + [self.post, self.dev]

    @data.setter
    @guard
    def data(self: Self, value: Any) -> None:
        self.pre, self.post, self.dev = parse_leg(value)

    @property
    def dev(self: Self) -> Optional[int]:
        return self._dev

    @dev.setter
    @guard
    def dev(self: Self, value: Any) -> None:
        self._dev = SimpleQualifierParser.DEV(value)

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isempty(self: Self) -> bool:
        return self.data == [None, None, None, None]

    def isprerelease(self: Self) -> bool:
        return {self.prephase, self.presubphase, self.dev} != {None}

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def post(self: Self) -> Optional[int]:
        return self._post

    @post.setter
    @guard
    def post(self: Self, value: Any) -> None:
        self._post = SimpleQualifierParser.POST(value)

    @property
    def pre(self: Self) -> Optional[str]:
        return [self._prephase, self._presubphase]

    @pre.setter
    @guard
    def pre(self: Self, value: Any) -> None:
        self._prephase, self._presubphase = parse_pre(value)

    @property
    def prephase(self: Self) -> Optional[str]:
        return self._prephase

    @prephase.setter
    def prephase(self: Self, value: Any) -> None:
        self[0] = value

    @property
    def presubphase(self: Self) -> Optional[int]:
        return self._presubphase

    @presubphase.setter
    def presubphase(self: Self, value: Any) -> None:
        self[1] = value
