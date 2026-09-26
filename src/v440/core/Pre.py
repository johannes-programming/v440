"""Provide the Pre class for pre-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Pre"]

from dataclasses import dataclass
from typing import Any, Self, SupportsIndex

from frozendict import frozendict
from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


@dataclass(frozen=True, kw_only=True)
class PreDeformat:
    clues: tuple[Clue, Clue, Clue]
    info: frozendict[str, Pre]

    def __and__(self: Self, other: Self, /) -> Self:
        return type(self)(
            clues=(
                self.clues[0] & other.clues[0],
                self.clues[1] & other.clues[1],
                self.clues[2] & other.clues[2],
            ),
            info=self.info | other.info,
        )

    def best(self: Self, /) -> str:
        matches: dict[str, str]
        pos: list[set[str]]
        sols: list[str]
        s: str
        way: tuple[Any, ...]
        pos = list()
        pos.append(self.clues[0].possible(hollow="a", short="A"))
        pos.append(self.clues[1].possible(hollow="b", short="B"))
        pos.append(self.clues[2].possible(hollow="rc", short="C"))
        sols = list()
        for way in iterprod(*pos):
            s = "".join(way)
            matches = Cfg.fullmatches("pre_f", s)
            if way == (matches["a_f"], matches["b_f"], matches["rc_f"]):
                sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]


class Pre(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[Any, ...]:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    def _deformat(self: Self, body: str, /) -> PreDeformat:
        clues: list[Clue]
        clues = [Clue(), Clue(), Clue()]
        if self:
            clues[("a", "b", "rc").index(self.lit)] = Clue.by_example(body)
        return PreDeformat(
            clues=(clues[0], clues[1], clues[2]),
            info=frozendict({body: self}),
        )

    @staticmethod
    def _deformat_origin() -> PreDeformat:
        return PreDeformat(
            clues=(Clue(), Clue(), Clue()),
            info=frozendict(),
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        a: Clue
        b: Clue
        matches: dict[str, str]
        rc: Clue
        matches = Cfg.fullmatches("pre_f", spec)
        a = Clue.by_spec(matches["a_f"])
        b = Clue.by_spec(matches["b_f"])
        rc = Clue.by_spec(matches["rc_f"])
        return a, b, rc

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        ans: str
        a: Clue
        b: Clue
        clue: Clue
        rc: Clue
        a, b, rc = parsed
        if self.lit == "a":
            clue = a
        elif self.lit == "b":
            clue = b
        elif self.lit == "rc":
            clue = rc
        else:
            return ""
        if clue.head == "":
            return self.lit + str(self.num)
        ans = clue.head
        if clue.sep != "?":
            ans += clue.sep
        if self.num or clue.mag:
            ans += format(self.num, f"0{clue.mag}d")
        return ans

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> str:
        return Cfg.cfg.phases[value]

    @property
    def packaging(self: Self, /) -> tuple[str, int] | None:
        if self:
            return self.lit, self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(
        self: Self, value: tuple[str, SupportsIndex] | None, /
    ) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.num = 0
            self.lit, self.num = value
