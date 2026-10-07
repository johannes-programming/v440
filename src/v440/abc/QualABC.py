"""Provide the QualABC abstract base for qualified v440 classes."""

from __future__ import annotations

__all__: list[str] = ["QualABC"]

import operator
import string as string_
from abc import abstractmethod
from typing import Any, Generic, Literal, Self, SupportsIndex, TypeVar

from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC

Lit = TypeVar("Lit", bound=str)


class QualABC(NestedABC, Generic[Lit]):
    """Define shared literal-and-number behavior for release qualifiers."""

    _lit: Lit | Literal[""]
    _num: int
    __slots__ = ("_lit", "_num")

    @abstractmethod
    def _cmp(self: Self, /) -> Any: ...

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Return factories for the qualifier literal and number fields."""
        return dict(_lit=str, _num=int)

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Lit: ...

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a qualifier string into its normalized literal and number fields."""
        literal: str
        number_text: str
        if value == "":
            self._lit = ""
            self._num = 0
            return
        literal = value.rstrip(string_.digits)
        number_text = value[len(literal) :]
        if literal == "-":
            if not number_text:
                raise ValueError
            self._lit = self._lit_parse("-")
            self._num = int(number_text)
            return
        literal = literal.replace("-", ".")
        literal = literal.replace("_", ".")
        if literal.endswith("."):
            literal = literal[:-1]
        if literal.startswith("."):
            literal = literal[1:]
        if not literal:
            raise ValueError
        self._lit = self._lit_parse(literal)
        self._num = int("0" + number_text)

    def _todict(self: Self, /) -> dict[str, Any]:
        """Return the qualifier literal and number by public name."""
        return dict(lit=self.lit, num=self.num)

    @property
    def lit(self: Self, /) -> Lit | Literal[""]:
        """Return the normalized qualifier literal."""
        return self._lit

    @lit.setter
    @setter
    def lit(self: Self, value: object, /) -> None:
        """Normalize and assign the qualifier literal."""
        literal: str
        literal = str(value).lower()
        if literal:
            self._lit = self._lit_parse(literal)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""

    @property
    def num(self: Self, /) -> int:
        """Return the nonnegative qualifier serial number."""
        return self._num

    @num.setter
    @setter
    def num(self: Self, value: SupportsIndex, /) -> None:
        """Validate and assign the nonnegative qualifier serial number."""
        number: int
        number = operator.index(value)
        if number < 0:
            raise ValueError
        if number and not self.lit:
            self.string = number
        else:
            self._num = number
