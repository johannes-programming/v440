"""Provide the Pre class for pre-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Pre"]

from typing import Any, Self, SupportsIndex

from v440._deformatting.Clue import Clue
from v440._deformatting.PreRestrictor import PreRestrictor
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Pre(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[Any, ...]:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    def _deformat(self: Self, body: str, /) -> PreRestrictor:
        return PreRestrictor((body,))

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

    def _format_parsed(self: Self, /, *parsed: Any) -> str:
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
        if self.num or clue.mag:
            ans += format(self.num, f"0{clue.mag}d")
        return ans

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> str:
        return Cfg.cfg.data["phases"][value]  # type: ignore[no-any-return]

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
