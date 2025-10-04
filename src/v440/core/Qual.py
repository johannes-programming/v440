from __future__ import annotations

import operator
from typing import *

import setdoc
from overloadable import Overloadable

from v440._utils.guarding import guard
from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Pre import Pre
from v440.core.Dev import Dev

__all__ = ["Qual"]


class Qual(SlotStringer):

    __slots__ = ("_pre", "_post", "_dev")
    string: str
    pre: Pre
    post: Optional[int]
    dev: Dev

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.string)

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> str:
        self._pre = Pre()
        self._post = None
        self._dev = Dev()
        argc: int = len(args) + len(kwargs)
        keys: set = set(kwargs.keys())
        if argc <= 1 and keys <= {"string"}:
            return "string"
        return "pre"

    @__init__.overload("string")
    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self.string = string

    @__init__.overload("pre")
    @setdoc.basic
    def __init__(
        self: Self,
        pre: Any = "",
        post: Any = None,
        dev: Any = "",
    ) -> None:
        self.pre.string = pre
        self.post = post
        self.dev.string = dev

    def _cmp(self: Self) -> list:
        ans: list = list()
        if self.prephase:
            ans += [self.prephase, self.prenum]
        elif self.post is not None:
            ans += ["z", float("inf")]
        elif not self.dev:
            ans += ["z", float("inf")]
        else:
            ans += ["", -1]
        ans.append(-1 if self.post is None else self.post)
        ans.append(self.dev)
        return ans

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        ans: str = self.pre.string
        if self.post is not None:
            ans += ".post%s" % self.post
        ans += self.dev.string
        return ans

    def _string_fset(self: Self, value: str) -> None:
        v: str = value
        m: Any
        x: Any
        y: Any
        self.dev.string = ""
        self.post = None
        self.pre.string = ""
        while v:
            m = Pattern.QUALIFIERS.leftbound.search(v)
            v = v[m.end() :]
            if m.group("N"):
                self.post = int(m.group("N"))
                continue
            x = m.group("l")
            y = m.group("n")
            if x == "dev":
                self.dev.phase = "dev"
                self.dev.num = int(y)
                continue
            if x in ("post", "r", "rev"):
                self.post = int(y)
                continue
            self.pre.string = x + y

    def _todict(self: Self) -> dict:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self) -> Dev:
        "This property represents the stage of development."
        return self._dev

    def isdevrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a dev-release."
        return bool(self.dev)

    def isprerelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a pre-release."
        return self.pre.phase != "" or bool(self.dev)

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
    def pre(self: Self) -> str:
        return self._pre
