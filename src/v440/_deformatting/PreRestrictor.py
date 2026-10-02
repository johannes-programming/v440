"""Provide the Pre class for pre-releases in v440."""

from __future__ import annotations

__all__: list[str] = ["PreRestrictor"]

from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING, Self

from v440._deformatting.inactive_specs import inactive_specs
from v440._deformatting.matching_specs import matching_specs
from v440._deformatting.token_specs import token_specs

if TYPE_CHECKING:
    from v440.core.Pre import Pre


@dataclass(frozen=True)
class PreRestrictor:
    strings: tuple[str, ...] = ()

    def best(self: Self, /) -> str:
        from v440.core.Pre import Pre

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
    ) -> Self:
        """Return all potentially shortest pre-format specs for the examples."""

        token_groups: list[tuple[str, ...]]

        if not objects:
            return cls(("",))
        if not any(objects):
            return cls(("",))

        token_groups = []
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
