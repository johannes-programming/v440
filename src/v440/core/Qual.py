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
    """Model the pre-, post-, and development qualifiers of a version."""

    Pre: Final[type[Pre_]] = Pre_
    Post: Final[type[Post_]] = Post_
    Dev: Final[type[Dev_]] = Dev_
    _pre: Pre_
    _post: Post_
    _dev: Dev_

    __slots__ = ("_pre", "_post", "_dev")

    def _cmp(self: Self, /) -> tuple[str, int, Post_, Dev_]:
        """Return the comparison key for this value."""
        ans: tuple[str, int]
        if self.pre:
            ans = (self.pre.lit, self.pre.num)
        elif self.post or not self.dev:
            ans = ("z", 0)
        else:
            ans = ("", 0)
        return ans + (self.post, self.dev)

    def _deformat(self: Self, body: str, /) -> QualRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
        return QualRestrictor.by_string(body)

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Parse a format specification into normalized rendering fields."""
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
        """Render this value from normalized format fields."""
        ans: str
        ans = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Return factories for the nested fields owned by this class."""
        return dict(_pre=Pre_, _post=Post_, _dev=Dev_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

    def _todict(self: Self, /) -> dict[str, Any]:
        """Return this instance's nested fields by public name."""
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self, /) -> Dev_:
        "This property represents the stage of development."
        return self._dev

    @dev.setter
    @setter
    def dev(self: Self, value: object, /) -> None:
        """Update the development qualifier from the supplied value."""
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
        """Return the post-release qualifier."""
        return self._post

    @post.setter
    @setter
    def post(self: Self, value: object, /) -> None:
        """Update the post-release qualifier from the supplied value."""
        self.post.string = value

    @property
    def pre(self: Self, /) -> Pre_:
        """Return the pre-release qualifier."""
        return self._pre

    @pre.setter
    @setter
    def pre(self: Self, value: object, /) -> None:
        """Update the pre-release qualifier from the supplied value."""
        self.pre.string = value
