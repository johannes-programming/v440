"""Provide the Dev class for developmental releases in v440."""

from __future__ import annotations

__all__: list[str] = ["DevRestrictor"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from v440._deformatting.inactive_specs import inactive_specs
from v440._deformatting.matching_specs import matching_specs
from v440._deformatting.token_specs import token_specs

if TYPE_CHECKING:
    from v440.core.Dev import Dev


@dataclass(frozen=True)
class DevRestrictor:
    strings: tuple[str, ...] = ()

    def best(self: Self, /) -> str:
        from v440.core.Dev import Dev

        objects = tuple(Dev(string=body) for body in self.strings)
        candidates = DevCandidatePool.by_specs(objects, self.strings, "exact")
        if not candidates:
            raise ValueError
        return candidates[0]

    def union(self: Self, other: Self, /) -> Self:
        return type(self)(tuple(sorted(set(self.strings + other.strings))))


class DevCandidatePool(tuple[str]):
    @classmethod
    def by_specs(
        cls: type[Self],
        objects: tuple[Dev, ...],
        strings: tuple[str, ...],
        relation: str,
        /,
    ) -> Self:
        if not objects:
            return cls(("",))
        active = next((i for i, obj in enumerate(objects) if obj), None)
        specs = (
            inactive_specs("dev_f")
            if active is None
            else token_specs("dev_f", strings[active])
        )
        data = matching_specs(
            objects,
            strings,
            specs,
            relation,  # type: ignore[arg-type]
        )
        return cls(data)
