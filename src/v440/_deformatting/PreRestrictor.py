from __future__ import annotations

__all__: list[str] = ["PreRestrictor"]

from collections import abc
from itertools import product
from typing import Literal, NamedTuple, Self

from v440._deformatting.Clue import Clue
from v440._deformatting.QualABCRestrictor import QualABCRestrictor
from v440._utils.Cfg import Cfg


def _spec_sort_key(item: str, /) -> tuple[int, str]:
    return len(item), item


def _options(
    name: str, pattern: str, restrictor: QualABCRestrictor, /
) -> tuple[str, ...]:
    ans: set[str]
    magnitudes: abc.Iterable[int]
    pair = restrictor.pair
    if pair is None:
        return tuple(Cfg.cfg.data["inactive-specs"][pattern])

    if pair.num > 0:
        magnitudes = (pair.num,)
    elif pair.num == 0:
        magnitudes = (0,)
    else:
        magnitudes = range(1 - pair.num)

    ans = set()
    for magnitude in magnitudes:
        spec = pair.lit + "#" * magnitude
        try:
            Cfg.fullmatches(pattern, spec)
        except Exception:
            continue
        ans.add(spec)

    # With an empty clue, Pre uses its canonical phase spelling and emits the
    # natural decimal number. This reproduces the canonical, non-omitted forms
    # that need at most one digit of zero-padding (``a0``, ``a1``, ``a10``,
    # and analogues).
    if pair.lit == name and pair.num != 0 and pair.num <= 1:
        ans.add("")

    return tuple(sorted(ans, key=_spec_sort_key))


def _valid(name: str, restrictor: QualABCRestrictor, clue: Clue, /) -> bool:
    pair = restrictor.pair
    if pair is None:
        return True

    if clue.head == "":
        return pair.lit == name and pair.num != 0 and pair.num <= 1
    if clue.head != pair.lit:
        return False
    if pair.num > 0:
        return clue.mag == pair.num
    if pair.num == 0:
        return clue.mag == 0
    return clue.mag <= -pair.num


class PreRestrictor(NamedTuple):
    a: QualABCRestrictor = QualABCRestrictor()
    b: QualABCRestrictor = QualABCRestrictor()
    rc: QualABCRestrictor = QualABCRestrictor()

    def best(self: Self, /) -> str:
        """Return the shortest pre-release format represented by this state."""

        names = ("a", "b", "rc")
        patterns = ("a_f", "b_f", "rc_f")
        restrictors = (self.a, self.b, self.rc)

        groups = tuple(
            _options(name, pattern, restrictor)
            for name, pattern, restrictor in zip(names, patterns, restrictors)
        )
        candidates: set[str] = set()
        for parts in product(*groups):
            spec = "".join(parts)
            try:
                matches = Cfg.fullmatches("pre_f", spec)
            except Exception:
                continue
            clues = tuple(
                Clue.by_spec(matches[pattern]) for pattern in patterns
            )
            if all(
                _valid(name, restrictor, clue)
                for name, restrictor, clue in zip(names, restrictors, clues)
            ):
                candidates.add(spec)

        if not candidates:
            raise ValueError
        return min(candidates, key=_spec_sort_key)

    @classmethod
    def by_string(
        cls: type[Self], text: str, /, *, name: Literal["", "a", "b", "rc"]
    ) -> Self:
        if name:
            return cls(**{name: QualABCRestrictor.by_string(text)})
        else:
            return cls()

    def union(self: Self, other: Self, /) -> Self:
        return type(self)(
            a=self.a.union(other.a),
            b=self.b.union(other.b),
            rc=self.rc.union(other.rc),
        )
