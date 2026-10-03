"""Provide the Dev class for developmental releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Dev"]

import operator
from typing import Literal, Self, SupportsIndex

from v440._deformatting.DevRestrictor import DevRestrictor
from v440._deformatting.QualABCPair import QualABCPair
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Dev(QualABC[Literal["dev"]]):

    """Represent Dev."""
    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[int] | tuple[int, int]:
        """Handle cmp."""
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    def _deformat(self: Self, string: str, /) -> DevRestrictor:
        """Handle deformat."""
        return DevRestrictor.by_string(string)

    @classmethod
    def _format_parse(
        cls: type[Self], spec: str, /
    ) -> tuple[QualABCPair | None]:
        """Handle format parse."""
        pair: QualABCPair
        matches: dict[str, str]
        if spec == "":
            return (None,)
        matches = Cfg.fullmatches("dev_f", spec)
        pair = QualABCPair(
            lit=matches["dev_head_f"],
            mag=len(matches["dev_num_f"]),
        )
        return (pair,)

    def _format_parsed(self: Self, pair: QualABCPair | None, /) -> str:
        """Handle format parsed."""
        if not self:
            return ""
        if pair is None:
            return ".dev" + str(self.num)
        if self.num or pair.mag:
            return pair.lit + format(self.num, f"0{pair.mag}d")
        return pair.lit

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Literal["dev"]:
        """Handle lit parse."""
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self, /) -> int | None:
        """Perform packaging."""
        if self:
            return self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        """Perform packaging."""
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
