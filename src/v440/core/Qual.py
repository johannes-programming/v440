"""Provide the Qual class for qualified version parts in v440."""

from __future__ import annotations

from v440._deformatting.QualRestrictor import QualRestrictor

__all__: list[str] = ["Qual"]

from typing import Any, Final, Self

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Dev import Dev as Dev_
from v440.core.Post import Post as Post_
from v440.core.Pre import Pre as Pre_


class Qual(NestedABC):
    """Represent Qual."""

    Pre: Final[type[Pre_]] = Pre_
    Post: Final[type[Post_]] = Post_
    Dev: Final[type[Dev_]] = Dev_
    _pre: Pre_
    _post: Post_
    _dev: Dev_

    __slots__ = ("_pre", "_post", "_dev")

    def _cmp(self: Self, /) -> tuple[str, int, Post_, Dev_]:
        """Handle cmp."""
        ans: tuple[str, int]
        if self.pre:
            ans = (self.pre.lit, self.pre.num)
        elif self.post or not self.dev:
            ans = ("z", 0)
        else:
            ans = ("", 0)
        return ans + (self.post, self.dev)

    def _deformat(self: Self, body: str, /) -> QualRestrictor:
        """Handle deformat."""
        return QualRestrictor.by_string(body)

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Handle format parse."""
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
        """Handle format parsed."""
        ans: str
        ans = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Handle init factories."""
        return dict(_pre=Pre_, _post=Post_, _dev=Dev_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Handle string fset."""
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

    def _todict(self: Self, /) -> dict[str, Any]:
        """Handle todict."""
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self, /) -> Dev_:
        "This property represents the stage of development."
        return self._dev

    @dev.setter
    @setter
    def dev(self: Self, value: object, /) -> None:
        """Perform dev."""
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
        """Perform post."""
        return self._post

    @post.setter
    @setter
    def post(self: Self, value: object, /) -> None:
        """Perform post."""
        self.post.string = value

    @property
    def pre(self: Self, /) -> Pre_:
        """Perform pre."""
        return self._pre

    @pre.setter
    @setter
    def pre(self: Self, value: object, /) -> None:
        """Perform pre."""
        self.pre.string = value
