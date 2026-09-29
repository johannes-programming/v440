"""Provide the Qual class for qualified version parts in v440."""

from __future__ import annotations

__all__: list[str] = ["Qual"]

from typing import Any, Final, NamedTuple, Self

from iterprod import iterprod

from v440._deformatting.Clue import Clue
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Dev import Dev as Dev_
from v440.core.Post import Post as Post_
from v440.core.Pre import Pre as Pre_


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

    def _deformat(self: Self, body: str, /) -> QualAccumulation:
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
        return QualAccumulation(*clues)

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual_f", spec)
        return (
            matches["pre_f"],
            matches["post_f"],
            matches["dev_f"],
        )

    def _format_parsed(
        self: Self, pre_f: str, post_f: str, dev_f: str, /
    ) -> str:
        ans: str
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


class QualAccumulation(NamedTuple):

    a: Clue = Clue()
    b: Clue = Clue()
    rc: Clue = Clue()
    post: Clue = Clue()
    dev: Clue = Clue()

    def intersection(self: Self, other: Self, /) -> Self:
        return type(self)(*(x.intersection(y) for x, y in zip(self, other)))

    def best(self: Self, /) -> str:
        s: str
        t: str
        matches: dict[str, str]
        parts: list[str]
        pos: list[set[str]]
        sols: list[str]
        way: tuple[Any, ...]
        pos = list()
        pos.append(self[0].possible("A", hollow="a"))
        pos.append(self[1].possible("B", hollow="b"))
        pos.append(self[2].possible("C", hollow="rc"))
        pos.append(self[3].possible("-", "R", hollow=".post"))
        pos.append(self[4].possible("DEV", hollow=".dev"))
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
