"""Provide the Post class for post-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Post"]

import operator
from dataclasses import dataclass
from typing import Any, Self, SupportsIndex

from v440._deformatting.Clue import Clue
from v440._deformatting.inactive_specs import inactive_specs
from v440._deformatting.matching_specs import matching_specs
from v440._deformatting.token_specs import token_specs
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Post(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> int:
        if self.lit:
            return self.num
        else:
            return -1

    def _deformat(self: Self, body: str, /) -> PostAccumulation:
        return PostAccumulation((body,))

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        clue: Clue
        matches: dict[str, str]
        matches = Cfg.fullmatches("post_f", spec)
        clue = Clue(
            head=matches["post_head_f"] or matches["post_hyphen_f"],
            mag=len(matches["post_num_f"]),
        )
        return (clue,)

    def _format_parsed(self: Self, /, *parsed: Any) -> str:
        clue: Clue
        (clue,) = parsed
        if not self:
            return ""
        if "" == clue.head:
            return ".post" + str(self.num)
        if self.num or clue.mag or "-" == clue.head:
            return clue.head + format(self.num, f"0{clue.mag}d")
        return clue.head

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> str:
        if value in ("-", "post", "r", "rev"):
            return "post"
        else:
            raise ValueError

    @property
    def packaging(self: Self, /) -> int | None:
        return self.num if self else None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "post"
            self.num = operator.index(value)


@dataclass(frozen=True)
class PostAccumulation:
    strings: tuple[str, ...] = ()

    def best(self: Self, /) -> str:
        objects = tuple(Post(string=body) for body in self.strings)
        candidates = PostCandidatePool.by_specs(objects, self.strings, "exact")
        if not candidates:
            raise ValueError
        return candidates[0]

    def union(self: Self, other: Self, /) -> Self:
        return type(self)(tuple(sorted(set(self.strings + other.strings))))


class PostCandidatePool(tuple[str]):
    @classmethod
    def by_specs(
        cls: type[Self],
        objects: tuple[Post, ...],
        strings: tuple[str, ...],
        relation: str,
        /,
    ) -> tuple[str, ...]:
        if not objects:
            return ("",)
        active = next((i for i, obj in enumerate(objects) if obj), None)
        specs = (
            inactive_specs("post_f")
            if active is None
            else token_specs("post_f", strings[active])
        )
        data = matching_specs(
            objects,
            strings,
            specs,
            relation,  # type: ignore[arg-type]
        )
        return cls(data)
