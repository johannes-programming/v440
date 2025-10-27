from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Cfg import Cfg
from v440._utils.SlotStringer import SlotStringer
from v440.core.Dev import Dev
from v440.core.Post import Post
from v440.core.Pre import Pre
from v440._utils.QualSpec import QualSpec
from iterprod import iterprod

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

    @classmethod
    def _deformat(cls: type, info: dict[str, Self], /) -> str:
        i:int
        s: str
        o: Self
        parsed:list[QualSpec]
        table: list[QualSpec]
        pos:list[set[str]]
        sols:list[str]
        way:tuple
        table = [QualSpec("", 0) for i in range(5)]
        for s, o in info.items():
            parsed = cls._deformat_parse_example(s, phase=o.pre.lit)
            for i in range(5):
                table[i] &= parsed[i]
        pos = list()
        pos.append(table[i].options(hollow="a", short="a"))
        pos.append(table[i].options(hollow="b", short="b"))
        pos.append(table[i].options(hollow="rc", short="c"))
        pos.append(table[i].options(hollow=".post", short="r"))
        pos.append(table[i].options(hollow=".dev", short="dev"))
        sols = list()
        for way in iterprod(*pos):
            s=""
            for i in range(5):
                s += way[i]
            parsed = cls._deformat_parse_spec(s)
            try:
                table & parsed
            except Exception:
                continue
            sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]

    @classmethod
    def _deformat_parse_example(cls:type, value:str, /, *, phase:str) -> dict[str, QualSpec]:
        ans:list[QualSpec]
        matches:dict[str, str]
        i:int
        matches = Cfg.fullmatches("qual", value)
        ans = list()
        ans.append(QualSpec("", 0))
        ans.append(QualSpec("", 0))
        ans.append(QualSpec("", 0))
        if phase:
            i = ("a", "b", "rc").index(phase)
            ans[i] = QualSpec.by_example(matches["pre"])
        ans.append(QualSpec.by_example(matches["post"]))
        ans.append(QualSpec.by_example(matches["dev"]))
        return ans

    @classmethod
    def _deformat_parse_spec(cls:type, value:str) -> dict[str, QualSpec]:
        ans:list[QualSpec]
        matches:dict[str, str]
        s:str
        matches = Cfg.fullmatches("qual_f", value)
        ans = list()
        for s in ("a", "b", "rc", "post", "dev"):
            ans.append(QualSpec.by_spec(matches[s + "_f"]))
        return ans

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        matches: dict = Cfg.fullmatches("qual_f", spec)
        return dict(
            pre_f=matches["pre_f"],
            post_f=matches["post_f"],
            dev_f=matches["dev_f"],
        )

    def _format_parsed(self: Self, *, pre_f: str, post_f: str, dev_f: str) -> str:
        ans: str = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        matches: dict = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

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
