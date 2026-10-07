"""Provide the Public class for public version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Public"]


import string as string_
from typing import Any, Final, Self

from v440._deformatting.PublicRestrictor import PublicRestrictor
from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC
from v440.core.Base import Base as Base_
from v440.core.Qual import Qual as Qual_


class Public(NestedABC):
    """Model the public portion of a PEP 440 version."""

    Base: Final[type[Base_]] = Base_
    Qual: Final[type[Qual_]] = Qual_
    _base: Base_
    _qual: Qual_

    __slots__ = ("_base", "_qual")

    def _cmp(self: Self, /) -> tuple[Base_, Qual_]:
        """Return the comparison key for this value."""
        return self.base, self.qual

    def _deformat(self: Self, body: str, /) -> PublicRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
        base: str
        qual: str
        base, qual = split_public(body)
        return PublicRestrictor(
            base=self.base._deformat(base),
            qual=self.qual._deformat(qual),
        )

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Parse a format specification into normalized rendering fields."""
        split_index: int
        split_index = int(spec.lower().startswith("v"))
        while split_index < len(spec):
            if spec[split_index] in "#!.":
                split_index += 1
            else:
                break
        if (
            split_index != 0
            and spec[split_index - 1] == "."
            and split_index != len(spec)
            and spec[split_index] not in "-_"
        ):
            split_index -= 1
        return spec[:split_index], spec[split_index:]

    def _format_parsed(self: Self, base_f: str, qual_f: str, /) -> str:
        """Render this value from normalized format fields."""
        return format(self.base, base_f) + format(self.qual, qual_f)

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Return factories for the nested fields owned by this class."""
        return dict(_base=Base_, _qual=Qual_)

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
        self.base.string, self.qual.string = split_public(value)

    def _todict(self: Self, /) -> dict[str, Any]:
        """Return this instance's nested fields by public name."""
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self, /) -> Base_:
        """Return the public-version base component."""
        return self._base

    @base.setter
    @setter
    def base(self: Self, value: object, /) -> None:
        """Return the public-version base component."""
        self.base.string = value

    packaging = NestedABC.string

    @property
    def qual(self: Self, /) -> Qual_:
        """Return the public-version qualifier component."""
        return self._qual

    @qual.setter
    @setter
    def qual(self: Self, value: object, /) -> None:
        """Replace the public-version qualifier from the supplied value."""
        self.qual.string = value


def split_public(value: str, /) -> tuple[str, str]:
    """Split a public version string into base and qualifier components."""
    split_index: int
    split_index = int(value.lower().startswith("v"))
    while split_index < len(value):
        if value[split_index] in (string_.digits + "!."):
            split_index += 1
        else:
            break
    if split_index and (value[split_index - 1] == "."):
        split_index -= 1
    return value[:split_index], value[split_index:]
