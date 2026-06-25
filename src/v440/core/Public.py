"""Provide the Public class for public version identifiers in v440."""

from __future__ import annotations

__all__ = ["Public"]

import string as string_
from typing import Any, Final, Self

from v440.abc.NestedABC import NestedABC
from v440.core.Base import Base as Base_
from v440.core.Qual import Qual as Qual_


class Public(NestedABC):

    Base: Final[type[Base_]] = Base_
    Qual: Final[type[Qual_]] = Qual_
    _base: Base_
    _qual: Qual_

    __slots__ = ("_base", "_qual")

    def _cmp(self: Self) -> tuple[Base_, Qual_]:
        return self.base, self.qual

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self]) -> str:
        bases: set[str]
        quals: set[str]
        x: str
        y: str
        bases = set()
        quals = set()
        for x, y in map(cls._split, info.keys()):
            bases.add(x)
            quals.add(y)
        x = Base_.deformat(*bases)
        y = Qual_.deformat(*quals)
        return x + y

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
    def _init_factories(cls: type[Self]) -> dict[str, Any]:
        return dict(_base=Base_, _qual=Qual_)

    @classmethod
    def _split(cls: type[Self], value: str) -> tuple[str, str]:
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

    def _string_fset(self: Self, value: str) -> None:
        self.base.string, self.qual.string = self._split(value)

    def _todict(self: Self) -> dict[str, Any]:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self) -> Base_:
        "This property represents the version base."
        return self._base

    @base.setter
    def base(self: Self, value: object) -> None:
        self.base.string = value

    packaging = NestedABC.string

    @property
    def qual(self: Self) -> Qual_:
        "This property represents the qualification."
        return self._qual

    @qual.setter
    def qual(self: Self, value: object) -> None:
        self.qual.string = value
