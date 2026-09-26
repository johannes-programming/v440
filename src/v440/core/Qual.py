"""Provide the Qual class for qualified version parts in v440."""

from __future__ import annotations

__all__: list[str] = ["Qual"]

import operator
from dataclasses import dataclass
from typing import Any, Final, Self

from frozendict import frozendict
from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Dev import Dev as Dev_
from v440.core.Post import Post as Post_
from v440.core.Pre import Pre as Pre_


@dataclass(frozen=True, kw_only=True)
class QualDeformat:

    clues: tuple[Clue, ...] = (Clue(), Clue(), Clue(), Clue(), Clue())
    info: frozendict[str, Qual] = frozendict()

    def __and__(self: Self, other: Self, /) -> Self:
        return type(self)(
            info=self.info | other.info,
            clues=tuple(map(operator.and_, self.clues, other.clues)),
        )

    def best(self: Self, /) -> str:
        s: str
        t: str
        matches: dict[str, str]
        parts: list[str]
        pos: list[set[str]]
        sols: list[str]
        way: tuple[Any, ...]
        pos = list()
        pos.append(self.clues[0].possible(hollow="a", short="A"))
        pos.append(self.clues[1].possible(hollow="b", short="B"))
        pos.append(self.clues[2].possible(hollow="rc", short="C"))
        pos.append(self.clues[3].possible(hollow=".post", short="R"))
        pos.append(self.clues[4].possible(hollow=".dev", short="DEV"))
        sols = list()
        for way in iterprod(*pos):
            s = "".join(way)
            matches = Cfg.fullmatches("qual_f", s)
            parts = list()
            for t in ("a", "b", "rc", "post", "dev"):
                parts.append(matches[t + "_f"])
            if way == tuple(parts):
                sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]


class Qual(NestedABC):

    Pre: Final[type[Pre_]] = Pre_
    Post: Final[type[Post_]] = Post_
    Dev: Final[type[Dev_]] = Dev_
    _pre: Pre_
    _post: Post_
    _dev: Dev_

    __slots__ = ("_pre", "_post", "_dev")

    def _cmp(self: Self, /) -> tuple[str, int, Post_, Dev_]:
        ans: tuple[str, int]
        if self.pre:
            ans = (self.pre.lit, self.pre.num)
        elif self.post or not self.dev:
            ans = ("z", 0)
        else:
            ans = ("", 0)
        return ans + (self.post, self.dev)

    def _deformat(self: Self, body: str, /) -> QualDeformat:
        clues: list[Clue]
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", body)
        clues = list()
        if self.pre.lit == "":
            clues.append(Clue())
            clues.append(Clue())
            clues.append(Clue())
        if self.pre.lit == "a":
            clues.append(Clue.by_example(matches["pre"]))
            clues.append(Clue())
            clues.append(Clue())
        if self.pre.lit == "b":
            clues.append(Clue())
            clues.append(Clue.by_example(matches["pre"]))
            clues.append(Clue())
        if self.pre.lit == "rc":
            clues.append(Clue())
            clues.append(Clue())
            clues.append(Clue.by_example(matches["pre"]))
        clues.append(Clue.by_example(matches["post"]))
        clues.append(Clue.by_example(matches["dev"]))
        return QualDeformat(
            clues=tuple(clues),
            info=frozendict({body: self}),
        )

    @staticmethod
    def _deformat_origin() -> QualDeformat:
        return QualDeformat()

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual_f", spec)
        return (
            matches["pre_f"],
            matches["post_f"],
            matches["dev_f"],
        )

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        ans: str
        pre_f: str
        post_f: str
        dev_f: str
        pre_f, post_f, dev_f = parsed
        ans = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_pre=Pre_, _post=Post_, _dev=Dev_)

    def _string_fset(self: Self, value: str, /) -> None:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

    def _todict(self: Self, /) -> dict[str, Any]:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self, /) -> Dev_:
        "This property represents the stage of development."
        return self._dev

    @dev.setter
    @setter
    def dev(self: Self, value: object, /) -> None:
        self.dev.string = value

    def isdevrelease(self: Self, /) -> bool:
        "Return whether this instance denotes a dev-release."
        return bool(self.dev)

    def isprerelease(self: Self, /) -> bool:
        "Return whether this instance denotes a pre-release."
        return bool(self.pre) or bool(self.dev)

    def ispostrelease(self: Self, /) -> bool:
        "Return whether this instance denotes a post-release."
        return bool(self.post)

    packaging = NestedABC.string

    @property
    def post(self: Self, /) -> Post_:
        return self._post

    @post.setter
    @setter
    def post(self: Self, value: object, /) -> None:
        self.post.string = value

    @property
    def pre(self: Self, /) -> Pre_:
        return self._pre

    @pre.setter
    @setter
    def pre(self: Self, value: object, /) -> None:
        self.pre.string = value
