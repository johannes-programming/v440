from __future__ import annotations

import operator
from functools import reduce
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440.abc.QualABC import QualABC

__all__ = ["Dev"]


class Dev(QualABC):

    __slots__ = ()

    def _cmp(self: Self) -> tuple:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        clues: Iterable[Clue]
        clues = map(Clue.by_example, info.keys())
        return reduce(operator.and_, clues, Clue()).solo(".dev")

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        clue: Clue
        matches: dict[str, str]
        matches = Cfg.fullmatches("dev_f", spec)
        clue = Clue(
            matches["dev_head_f"],
            matches["dev_sep_f"],
            len(matches["dev_num_f"]),
        )
        return (clue,)

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        clue: Clue
        (clue,) = parsed
        if not self:
            return ""
        if "" == clue.head:
            return ".dev" + str(self.num)
        if 0 == clue.mag and 0 == self.num:
            return clue.head
        return clue.head + clue.sep + format(self.num, f"0{clue.mag}d")

    @classmethod
    def _lit_parse(cls: type[Self], value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self) -> Optional[int]:
        if self:
            return self.num
        else:
            return None

    @packaging.setter
    def packaging(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
