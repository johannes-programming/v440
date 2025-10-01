from __future__ import annotations

import operator
from typing import *

import setdoc
from overloadable import Overloadable

from v440._utils import qualparse
from v440._utils.guarding import guard
from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer

__all__ = ["Qual"]


class Qual(SlotStringer):

    __slots__ = ("_prephase", "_presubphase", "_post", "_dev")

    string: str
    pre: tuple
    prephase: Optional[str]
    presubphase: Optional[int]
    post: Optional[int]
    dev: Optional[int]

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return self.string == ""

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> bool:
        if "string" in kwargs.keys():
            return True
        if len(args) <= 1 and len(kwargs) == 0:
            return True
        return False

    @__init__.overload(True)
    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._init_setup()
        self.string = string

    @__init__.overload(False)
    @setdoc.basic
    def __init__(
        self: Self,
        pre: Any = None,
        post: Any = None,
        dev: Any = None,
    ) -> None:
        self._init_setup()
        self.pre = pre
        self.post = post
        self.dev = dev

    def _init_setup(self: Self) -> None:
        self._prephase = None
        self._presubphase = None
        self._post = None
        self._dev = None

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

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
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

    def _string_fset(self: Self, value: str) -> None:
        v: str = value
        m: Any
        x: Any
        y: Any
        self.dev = None
        self.post = None
        pre: Any = (None, None)
        while v:
            m = Pattern.QUALIFIERS.leftbound.search(v)
            v = v[m.end() :]
            if m.group("N"):
                self.post = int(m.group("N"))
                continue
            x = m.group("l")
            y = m.group("n")
            if x == "dev":
                self.dev = int(y)
                continue
            if x in ("post", "r", "rev"):
                self.post = int(y)
                continue
            pre = x, y
        self.pre = pre

    def _todict(self: Self) -> dict:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self) -> Optional[int]:
        "This property represents the stage of development."
        return self._dev

    @dev.setter
    @guard
    def dev(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self._dev = None
            return
        self._dev: int = operator.index(value)
        if self._dev < 0:
            raise ValueError

    def isdevrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a dev-release."
        return self.dev is not None

    def isprerelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a pre-release."
        return {self.prephase, self.presubphase, self.dev} != {None}

    def ispostrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a post-release."
        return self.post is not None

    @property
    def post(self: Self) -> Optional[int]:
        return self._post

    @post.setter
    @guard
    def post(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self._post = None
            return
        self._post: int = abs(operator.index(value))

    @property
    def pre(self: Self) -> tuple:
        return self._prephase, self._presubphase

    @pre.setter
    @guard
    def pre(self: Self, value: Any) -> None:
        self._prephase, self._presubphase = qualparse.parse_pre(value)

    @property
    def prephase(self: Self) -> Optional[str]:
        return self._prephase

    @prephase.setter
    def prephase(self: Self, value: Any) -> None:
        self.pre = value, self.presubphase

    @property
    def presubphase(self: Self) -> Optional[int]:
        return self._presubphase

    @presubphase.setter
    def presubphase(self: Self, value: Any) -> None:
        self.pre = self.prephase, value
