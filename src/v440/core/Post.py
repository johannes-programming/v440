"""Provide the Post class for post-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Post"]

import operator
from typing import Literal, Self, SupportsIndex

from v440._deformatting.PostRestrictor import PostRestrictor
from v440._deformatting.QualABCPair import QualABCPair
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Post(QualABC[Literal["post"]]):

    """Represent Post."""
    __slots__ = ()

    def _cmp(self: Self, /) -> int:
        """Handle cmp."""
        if self.lit:
            return self.num
        else:
            return -1

    def _deformat(self: Self, string: str, /) -> PostRestrictor:
        """Handle deformat."""
        return PostRestrictor.by_string(string)

    @classmethod
    def _format_parse(
        cls: type[Self], spec: str, /
    ) -> tuple[QualABCPair | None]:
        """Handle format parse."""
        lit: str
        matches: dict[str, str]
        pair: QualABCPair
        matches = Cfg.fullmatches("post_f", spec)
        lit = matches["post_head_f"] or matches["post_hyphen_f"]
        if not lit:
            return (None,)
        pair = QualABCPair(
            lit=lit,
            mag=len(matches["post_num_f"]),
        )
        return (pair,)

    def _format_parsed(self: Self, pair: QualABCPair | None, /) -> str:
        """Handle format parsed."""
        if not self:
            return ""
        if pair is None:
            return ".post" + str(self.num)
        if self.num or pair.mag or "-" == pair.lit:
            return pair.lit + format(self.num, f"0{pair.mag}d")
        return pair.lit

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Literal["post"]:
        """Handle lit parse."""
        if value in ("-", "post", "r", "rev"):
            return "post"
        else:
            raise ValueError

    @property
    def packaging(self: Self, /) -> int | None:
        """Perform packaging."""
        return self.num if self else None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        """Perform packaging."""
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "post"
            self.num = operator.index(value)
