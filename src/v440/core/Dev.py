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
    """Store a development-release qualifier and its serial number."""

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[int] | tuple[int, int]:
        """Return the comparison key for an active or absent development qualifier."""
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    def _deformat(self: Self, string: str, /) -> DevRestrictor:
        """Infer formatting constraints from one development-qualifier rendering."""
        return DevRestrictor.by_string(string)

    @classmethod
    def _format_parse(
        cls: type[Self], spec: str, /
    ) -> tuple[QualABCPair | None]:
        """Parse a development-qualifier format specification into literal and width constraints."""
        matches: dict[str, str]
        pair: QualABCPair
        if spec == "":
            return (None,)
        matches = Cfg.fullmatches("dev_f", spec)
        pair = QualABCPair(
            lit=matches["dev_head"],
            mag=len(matches["dev_num_f"]),
        )
        return (pair,)

    def _format_parsed(self: Self, pair: QualABCPair | None, /) -> str:
        """Render the development qualifier from parsed literal and width constraints."""
        if not self:
            return ""
        if pair is None:
            return ".dev" + str(self.num)
        if self.num or pair.mag:
            return pair.lit + format(self.num, f"0{pair.mag}d")
        return pair.lit

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Literal["dev"]:
        """Validate and normalize a development-qualifier literal."""
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self, /) -> int | None:
        """Return the development serial in packaging-compatible form."""
        if self:
            return self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: SupportsIndex | None, /) -> None:
        """Replace the development qualifier from a packaging-compatible serial."""
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
