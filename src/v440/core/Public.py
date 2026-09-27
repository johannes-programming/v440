"""Provide the Public class for public version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Public"]


import string as string_
from dataclasses import dataclass
from typing import Any, Final, Self

from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Base import Base as Base_
from v440.core.Qual import Qual as Qual_


def split_public(value: str, /) -> tuple[str, str]:
    i: int
    i = int(value.lower().startswith("v"))
    while i < len(value):
        if value[i] in (string_.digits + "!."):
            i += 1
        else:
            break
    if i and (value[i - 1] == "."):
        i -= 1
    return value[:i], value[i:]


@dataclass(frozen=True, kw_only=True)
class PublicAccumulation:
    bases: frozenset[str]
    quals: frozenset[str]

    def __and__(self: Self, other: Self, /) -> Self:
        return type(self)(
            bases=self.bases | other.bases,
            quals=self.quals | other.quals,
        )

    def best(self: Self, /, *, forbids_empty: bool = False) -> str:
        ans: str
        ans = Base_.deformat(*self.bases) + Qual_.deformat(*self.quals)
        if forbids_empty and not ans:
            return "#"
        return ans


class Public(NestedABC):

    Base: Final[type[Base_]] = Base_
    Qual: Final[type[Qual_]] = Qual_
    _base: Base_
    _qual: Qual_

    __slots__ = ("_base", "_qual")

    def _cmp(self: Self, /) -> tuple[Base_, Qual_]:
        return self.base, self.qual

    def _deformat(self: Self, body: str, /) -> PublicAccumulation:
        base: str
        qual: str
        base, qual = split_public(body)
        return PublicAccumulation(
            bases=frozenset({base}),
            quals=frozenset({qual}),
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        i: int
        i = int(spec.lower().startswith("v"))
        while i < len(spec):
            if spec[i] in "#!.":
                i += 1
            else:
                break
        if (
            i != 0
            and spec[i - 1] == "."
            and i != len(spec)
            and spec[i] not in "-_"
        ):
            i -= 1
        return spec[:i], spec[i:]

    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> str:
        base_f: str
        qual_f: str
        base_f, qual_f = parsed
        return format(self.base, base_f) + format(self.qual, qual_f)

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        return dict(_base=Base_, _qual=Qual_)

    def _string_fset(self: Self, value: str, /) -> None:
        self.base.string, self.qual.string = split_public(value)

    def _todict(self: Self, /) -> dict[str, Any]:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self, /) -> Base_:
        "This property represents the version base."
        return self._base

    @base.setter
    @setter
    def base(self: Self, value: object, /) -> None:
        self.base.string = value

    packaging = NestedABC.string

    @property
    def qual(self: Self, /) -> Qual_:
        "This property represents the qualification."
        return self._qual

    @qual.setter
    @setter
    def qual(self: Self, value: object, /) -> None:
        self.qual.string = value
