"""Restrict pre-release segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["PreRestrictor"]

from collections import abc
from itertools import product
from typing import Literal, NamedTuple, Self

from v440._deformatting.QualABCPair import QualABCPair
from v440._deformatting.QualABCRestrictor import QualABCRestrictor
from v440._utils.Cfg import Cfg


class PreRestrictor(NamedTuple):
    """Track formatting constraints for pre-release qualifiers."""

    a: QualABCRestrictor = QualABCRestrictor()
    b: QualABCRestrictor = QualABCRestrictor()
    rc: QualABCRestrictor = QualABCRestrictor()

    def _options(self: Self, name: str, /) -> tuple[str, ...]:
        """Return format options for one pre-release phase."""
        options: set[str]
        magnitude: int
        magnitudes: abc.Iterable[int]
        pair: QualABCPair | None
        pattern: str
        spec: str
        pattern = name + "_f"
        pair = getattr(self, name).pair
        if pair is None:
            return tuple(Cfg.cfg.data["inactive-specs"][pattern])

        if pair.mag > 0:
            magnitudes = (pair.mag,)
        elif pair.mag == 0:
            magnitudes = (0,)
        else:
            magnitudes = range(1 - pair.mag)

        options = set()
        for magnitude in magnitudes:
            spec = pair.lit + "#" * magnitude
            try:
                Cfg.fullmatches(pattern, spec)
            except Exception:
                continue
            options.add(spec)

        # With an empty clue, Pre uses its canonical phase spelling and
        # emits the natural decimal number. This reproduces the canonical,
        # non-omitted forms that need at most one digit of zero-padding
        # (``a0``, ``a1``, ``a10``, and analogues).
        if pair.lit == name and pair.mag != 0 and pair.mag <= 1:
            options.add("")

        return tuple(sorted(options, key=_spec_sort_key))

    def _valid(
        self: Self,
        name: str,
        clue: QualABCRestrictor,
        /,
    ) -> bool:
        """Return whether a candidate clue reproduces the stored pre-release phase."""
        pair: QualABCPair
        pair = getattr(self, name).pair
        if pair is None:
            return True

        if clue.pair is None:
            return pair.lit == name and pair.mag != 0 and pair.mag <= 1
        if clue.pair.lit != pair.lit:
            return False
        if pair.mag > 0:
            return clue.pair.mag == pair.mag
        if pair.mag == 0:
            return clue.pair.mag == 0
        return clue.pair.mag <= -pair.mag

    def best(self: Self, /) -> str:
        """Return the shortest pre-release format for this state."""
        candidates: set[str]
        groups: tuple[tuple[str, ...], ...]
        matches: dict[str, str]
        names: tuple[str, str, str]
        parts: tuple[str, ...]
        spec: str
        names = ("a", "b", "rc")
        groups = tuple(map(self._options, names))
        candidates = set()
        for parts in product(*groups):
            spec = "".join(parts)
            try:
                matches = Cfg.fullmatches("pre_f", spec)
            except Exception:
                continue
            if not self._valid("a", QualABCRestrictor.by_spec(matches["a_f"])):
                continue
            if not self._valid("b", QualABCRestrictor.by_spec(matches["b_f"])):
                continue
            if not self._valid(
                "rc", QualABCRestrictor.by_spec(matches["rc_f"])
            ):
                continue
            candidates.add(spec)

        if not candidates:
            raise ValueError
        return min(candidates, key=_spec_sort_key)

    @classmethod
    def by_string(
        cls: type[Self], text: str, /, *, name: Literal["", "a", "b", "rc"]
    ) -> Self:
        """Infer formatting constraints from one observed rendering."""
        if name:
            return cls(**{name: QualABCRestrictor.by_string(text)})
        else:
            return cls()

    def union(self: Self, other: Self, /) -> Self:
        """Combine these constraints with another compatible observation."""
        return type(self)(
            a=self.a.union(other.a),
            b=self.b.union(other.b),
            rc=self.rc.union(other.rc),
        )


def _spec_sort_key(item: str, /) -> tuple[int, str]:
    """Order format specifications by length and then lexical value."""
    return len(item), item
