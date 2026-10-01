"""Provide the Pre class for pre-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["Pre"]

from dataclasses import dataclass
from itertools import product
from typing import Any, Self, SupportsIndex

from v440._deformatting.Clue import Clue
from v440._deformatting.inactive_specs import inactive_specs
from v440._deformatting.matching_specs import matching_specs
from v440._deformatting.token_specs import token_specs
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.QualABC import QualABC


class Pre(QualABC):

    __slots__ = ()

    def _cmp(self: Self, /) -> tuple[Any, ...]:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    def _deformat(self: Self, body: str, /) -> PreAccumulation:
        return PreAccumulation((body,))

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


@dataclass(frozen=True)
class PreAccumulation:
    strings: tuple[str, ...] = ()

    def best(self: Self, /) -> str:
        objects = tuple(Pre(string=body) for body in self.strings)
        candidates = PreCandidatePool.by_specs(objects, self.strings, "exact")
        if not candidates:
            raise ValueError
        return candidates[0]

    def union(self: Self, other: Self, /) -> Self:
        return type(self)(tuple(sorted(set(self.strings + other.strings))))


class PreCandidatePool(tuple[str]):
    @classmethod
    def by_specs(
        cls: type[Self],
        objects: tuple[Pre, ...],
        strings: tuple[str, ...],
        relation: str,
        /,
    ) -> tuple[str, ...]:
        """Return all potentially shortest pre-format specs for the examples."""

        if not objects:
            return ("",)
        if not any(objects):
            return ("",)

        token_groups: list[tuple[str, ...]] = []
        for lit, pattern in (("a", "a_f"), ("b", "b_f"), ("rc", "rc_f")):
            indexes = tuple(
                i for i, obj in enumerate(objects) if obj.lit == lit
            )
            if not indexes:
                token_groups.append(inactive_specs(pattern))
                continue
            sample = strings[indexes[0]]
            phase_objects = tuple(objects[i] for i in indexes)
            phase_bodies = tuple(strings[i] for i in indexes)
            token_group = matching_specs(
                phase_objects,
                phase_bodies,
                token_specs(pattern, sample),
                relation,  # type: ignore[arg-type]
            )
            token_groups.append(token_group)

        specs = ("".join(parts) for parts in product(*token_groups))
        data = matching_specs(
            objects,
            strings,
            specs,
            relation,  # type: ignore[arg-type]
        )
        return cls(data)
