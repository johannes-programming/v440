from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Dev import Dev
from v440.core.Post import Post
from v440.core.Pre import Pre
import string as string_

__all__ = ["Qual"]


class Qual(SlotStringer):

    __slots__ = ("_pre", "_post", "_dev")
    string: str
    packaging: str
    pre: Pre
    post: Post
    dev: Dev

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._pre = Pre()
        self._post = Post()
        self._dev = Dev()
        self.string = string

    def _cmp(self: Self) -> tuple:
        ans: tuple = ()
        if self.pre:
            ans += (self.pre.lit, self.pre.num)
        elif self.post is not None:
            ans += ("z", 0)
        elif self.dev is None:
            ans += ("z", 0)
        else:
            ans += ("", 0)
        ans += (self.post, self.dev)
        return ans

    def _format(self: Self, spec: str) -> str:
        if spec.strip(string_.ascii_letters + "0.-_"):
            raise ValueError
        j:int = self._format_parse_j(spec)
        i:int = self._format_parse_i(spec[:j])
        ans:str = format(self.pre, spec[:i])
        ans += format(self.post, spec[i:j])
        ans += format(self.dev, spec[j:])
        return ans

    @classmethod
    def _format_parse_i(cls:type, spec:str) -> tuple:
        i:int = -1
        x:str
        for x in ("post", "r", "rev"):
            i = spec.lower().find(x)
            if i != -1:
                break
        if i > 0 and spec[i] in ".-_":
            i -= 1
        if i != -1:
            return i
        x = spec.rstrip(string_.digits)
        if x == "-" or x.endswith("0-"):
            i = spec.rindex("-")
        else:
            i = len(spec)
        return i
    
    @classmethod
    def _format_parse_j(cls:type, spec:str) -> tuple:
        j:int = spec.lower().find("dev")
        if j == -1:
            j = len(spec)
        elif j and (spec[j - 1] in ".-_"):
            j -= 1
        return j

    def _string_fset(self: Self, value: str) -> None:
        m: Any = Pattern.QUAL.bound.search(value)
        self.pre.string = Pattern.none_empty(m.group("pre"))
        self.post.string = Pattern.none_empty(m.group("post"))
        self.dev.string = Pattern.none_empty(m.group("dev"))

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
        return bool(self.pre) or bool(self.dev)

    def ispostrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a post-release."
        return bool(self.post)

    @property
    def post(self: Self) -> Post:
        return self._post

    @property
    def pre(self: Self) -> Pre:
        return self._pre
