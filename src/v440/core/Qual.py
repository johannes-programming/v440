from __future__ import annotations

from typing import *

import setdoc
from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.QualSpec import QualSpec
from v440._utils.SlotStringer import SlotStringer
from v440.core.Dev import Dev
from v440.core.Post import Post
from v440.core.Pre import Pre

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
        i: int
        s: str
        t: str
        o: Self
        parsed: tuple[QualSpec]
        table: tuple[QualSpec]
        pos: list[set[str]]
        sols: list[str]
        way: tuple
        table = [QualSpec("", 0) for i in range(5)]
        for s, o in info.items():
            parsed = cls._deformat_parse_example(s, phase=o.pre.lit)
            table = cls._deformat_and(table, parsed)
        pos = list()
        pos.append(table[0].options(hollow="a", short="a"))
        pos.append(table[1].options(hollow="b", short="b"))
        pos.append(table[2].options(hollow="rc", short="c"))
        pos.append(table[3].options(hollow=".post", short="r"))
        pos.append(table[4].options(hollow=".dev", short="dev"))
        sols = list()
        for way in iterprod(*pos):
            s = ""
            for t in way:
                s += t
            parsed = cls._deformat_parse_spec(s)
            try:
                cls._deformat_and(table, parsed)
            except Exception:
                continue
            sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]

    @classmethod
    def _deformat_and(
        cls: type,
        table: list[QualSpec],
        parsed: list[QualSpec],
        /,
    ) -> list[QualSpec]:
        x: QualSpec
        y: QualSpec
        ans: list[QualSpec]
        ans: list[QualSpec] = list()
        for x, y in zip(table, parsed, strict=True):
            ans.append(x & y)
        return ans

    @classmethod
    def _deformat_parse_example(
        cls: type,
        value: str,
        /,
        *,
        phase: str,
    ) -> tuple[QualSpec]:
        specs: list[QualSpec]
        matches: dict[str, str]
        i: int
        matches = Cfg.fullmatches("qual", value)
        specs = list()
        specs.append(QualSpec("", 0))
        specs.append(QualSpec("", 0))
        specs.append(QualSpec("", 0))
        if phase:
            i = ("a", "b", "rc").index(phase)
            specs[i] = QualSpec.by_example(matches["pre"])
        specs.append(QualSpec.by_example(matches["post"]))
        specs.append(QualSpec.by_example(matches["dev"]))
        return tuple(specs)

    @classmethod
    def _deformat_parse_spec(
        cls: type,
        value: str,
        /,
    ) -> tuple[QualSpec]:
        specs: list[QualSpec]
        matches: dict[str, str]
        s: str
        matches = Cfg.fullmatches("qual_f", value)
        specs = list()
        for s in ("a", "b", "rc", "post", "dev"):
            specs.append(QualSpec.by_spec(matches[s + "_f"]))
        return tuple(specs)

    @classmethod
    def _format_parse(cls: type, spec: str, /) -> dict:
        matches: dict
        ans: dict
        s: str
        matches: dict = Cfg.fullmatches("qual_f", spec)
        ans: dict = dict()
        for s in ("pre_f", "post_f", "dev_f"):
            ans[s] = matches[s]
        return ans

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
