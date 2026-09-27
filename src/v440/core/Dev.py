"""Provide the Dev class for developmental releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Dev"]

import operator
from typing import Any, Self, SupportsIndex

from v440._deformat_abc.Clue import Clue
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class DevAccumulation(Clue):
    def best(self: Self, /, *, forbids_empty: bool = False) -> str:
        ans: str
        possible: set[str]
        ans = self.solo(".dev")
        if ans or not forbids_empty:
            return ans
        if not self.head:
            return "DEV"
        possible = self.possible(hollow=".dev", short="DEV") - {""}
        return min(possible, key=lambda x: (len(x), x))


class Dev(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[int] | tuple[int, int]:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    def _deformat(self: Self, body: str, /) -> DevAccumulation:
        return DevAccumulation.by_example(body)

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        clue: Clue
        matches: dict[str, str]
        matches = Cfg.fullmatches("dev_f", spec)
        clue = Clue(
            head=matches["dev_head_f"],
            mag=len(matches["dev_num_f"]),
        )
        return (clue,)

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        clue: Clue
        (clue,) = parsed
        if not self:
            return ""
        if "" == clue.head:
            return ".dev" + str(self.num)
        if self.num or clue.mag:
            return clue.head + format(self.num, f"0{clue.mag}d")
        return clue.head

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self, /) -> int | None:
        if self:
            return self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
