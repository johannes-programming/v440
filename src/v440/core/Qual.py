from __future__ import annotations

import operator
import string as string_
from typing import *

import setdoc
from overloadable import Overloadable

from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard
from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer

__all__ = ["Qual"]


class Qual(SlotStringer):

    __slots__ = ("_prephase", "_presubphase", "_post", "_dev")
    string: str
    pre: str
    prephase: str
    presubphase: int
    post: Optional[int]
    dev: Optional[int]

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return self.string == ""

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> bool:
        self._prephase = ""
        self._presubphase = 0
        self._post = None
        self._dev = None
        argc: int = len(args) + len(kwargs)
        keys: set = set(kwargs.keys())
        if argc <= 1 and keys.issubset({"string"}):
            return "string"
        if argc <= 3 and keys.issubset({"pre", "post", "dev"}):
            return "pre"
        return "slots"

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
        dev: Any = None,
    ) -> None:
        self.pre = pre
        self.post = post
        self.dev = dev

    @__init__.overload("slots")
    @setdoc.basic
    def __init__(
        self: Self,
        prephase: Any = "",
        presubphase: Any = 0,
        post: Any = None,
        dev: Any = None,
    ) -> None:
        self.prephase = prephase
        self.presubphase = presubphase
        self.post = post
        self.dev = dev

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
        ans: str = self.pre
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
        self.pre = ""
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
            self.pre = x + y

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
        return self.prephase != "" or self.dev is not None

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
        if "" == self.prephase:
            return ""
        return self.prephase + str(self.presubphase)

    @pre.setter
    @guard
    def pre(self: Self, value: Any) -> None:
        v: str = str(value).lower()
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        x: str = v.rstrip(string_.digits)
        v = v[len(x) :]
        q: bool = x.endswith(".")
        if q:
            if not v:
                raise ValueError
            x = x[:-1]
        p: bool = x.startswith(".")
        if p:
            x = x[1:]
        if x:
            self._prephase = Cfg.cfg.data["phases"][x]
            self._presubphase = int("0" + v)
        elif p or v:
            raise ValueError
        else:
            self._prephase = ""
            self._presubphase = 0

    @property
    def prephase(self: Self) -> str:
        return self._prephase

    @prephase.setter
    @guard
    def prephase(self: Self, value: Any) -> None:
        x: str = str(value).lower()
        if x != "":
            self._prephase = Cfg.cfg.data["phases"][x]
        elif self.presubphase:
            self.pre = self.presubphase  # raises error

    @property
    def presubphase(self: Self) -> Optional[int]:
        return self._presubphase

    @presubphase.setter
    @guard
    def presubphase(self: Self, value: Any) -> None:
        y: int = operator.index(value)
        if y < 0:
            raise ValueError
        if self.prephase:
            self._presubphase = y
        else:
            self.pre = y  # raises error
