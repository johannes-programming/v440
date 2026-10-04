"""Provide the Pre class for pre-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Pre"]

from typing import Any, Literal, Self, SupportsIndex

from v440._deformatting.PreRestrictor import PreRestrictor
from v440._deformatting.QualABCRestrictor import QualABCRestrictor
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Pre(QualABC[Literal["a", "b", "rc"]]):
    """Model a pre-release qualifier."""

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[Any, ...]:
        """Return the comparison key for this value."""
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    def _deformat(self: Self, string: str, /) -> PreRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
        return PreRestrictor.by_string(string, name=self.lit)

    @classmethod
    def _format_parse(
        cls: type[Self], spec: str, /
    ) -> tuple[QualABCRestrictor, QualABCRestrictor, QualABCRestrictor]:
        """Parse a format specification into normalized rendering fields."""
        alpha: QualABCRestrictor
        beta: QualABCRestrictor
        matches: dict[str, str]
        rc: QualABCRestrictor
        matches = Cfg.fullmatches("pre_f", spec)
        alpha = QualABCRestrictor.by_spec(matches["a_f"])
        beta = QualABCRestrictor.by_spec(matches["b_f"])
        rc = QualABCRestrictor.by_spec(matches["rc_f"])
        return alpha, beta, rc

    def _format_parsed(
        self: Self,
        alpha: QualABCRestrictor,
        beta: QualABCRestrictor,
        rc: QualABCRestrictor,
        /,
    ) -> str:
        """Render this value from normalized format fields."""
        restrictor: QualABCRestrictor
        if self.lit == "a":
            restrictor = alpha
        elif self.lit == "b":
            restrictor = beta
        elif self.lit == "rc":
            restrictor = rc
        else:
            return ""
        if restrictor.pair is None:
            return self.lit + str(self.num)
        if self.num or restrictor.pair.mag:
            return restrictor.pair.lit + format(
                self.num, f"0{restrictor.pair.mag}d"
            )
        else:
            return restrictor.pair.lit

    @classmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Literal["a", "b", "rc"]:
        """Normalize a qualifier literal to its canonical spelling."""
        return Cfg.cfg.data["phases"][value]  # type: ignore[no-any-return]

    @property
    def packaging(self: Self, /) -> tuple[str, int] | None:
        """Return the packaging-compatible representation of this value."""
        if self:
            return self.lit, self.num
        else:
            return None

    @packaging.setter
    @setter
    def packaging(
        self: Self, value: tuple[str, SupportsIndex] | None, /
    ) -> None:
        """Update this value from its packaging-compatible representation."""
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.num = 0
            self.lit, self.num = value
