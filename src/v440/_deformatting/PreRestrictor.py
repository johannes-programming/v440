from __future__ import annotations

__all__: list[str] = ["PreRestrictor"]

from typing import Literal, NamedTuple, Self

from v440._deformatting.QualABCRestrictor import QualABCRestrictor


class PreRestrictor(NamedTuple):
    a: QualABCRestrictor = QualABCRestrictor()
    b: QualABCRestrictor = QualABCRestrictor()
    rc: QualABCRestrictor = QualABCRestrictor()

    def best(self: Self, /) -> str:
        pass

    @classmethod
    def by_string(
        cls: type[Self], text: str, /, *, name: Literal["a", "b", "rc"]
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
