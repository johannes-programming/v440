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
    """Provide shared literal-and-number behavior for qualifier components."""

    _lit: Lit | Literal[""]
    _num: int
    __slots__ = ("_lit", "_num")

    @abstractmethod
    def _cmp(self: Self, /) -> Any: ...

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Return factories for the nested fields owned by this class."""
        return dict(_lit=str, _num=int)

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Lit: ...

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
        literal: str
        digits: str
        if value == "":
            self._lit = ""
            self._num = 0
            return
        literal = value.rstrip(string_.digits)
        digits = value[len(literal) :]
        if literal == "-":
            if not digits:
                raise ValueError
            self._lit = self._lit_parse("-")
            self._num = int(digits)
            return
        # PEP 440 accepts hyphen, underscore, and dot separators interchangeably;
        # normalize them before resolving aliases to the canonical literal.
        literal = literal.replace("-", ".")
        literal = literal.replace("_", ".")
        if literal.endswith("."):
            literal = literal[:-1]
        if literal.startswith("."):
            literal = literal[1:]
        if not literal:
            raise ValueError
        self._lit = self._lit_parse(literal)
        self._num = int("0" + digits)

    def _todict(self: Self, /) -> dict[str, Any]:
        """Return this instance's nested fields by public name."""
        return dict(lit=self.lit, num=self.num)

    @property
    def lit(self: Self, /) -> Lit | Literal[""]:
        """Return the canonical qualifier literal."""
        return self._lit

    @lit.setter
    @setter
    def lit(self: Self, value: object, /) -> None:
        """Normalize and assign the qualifier literal."""
        normalized_literal: str
        normalized_literal = str(value).lower()
        if normalized_literal:
            self._lit = self._lit_parse(normalized_literal)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""

    @property
    def num(self: Self, /) -> int:
        """Return the qualifier number."""
        return self._num

    @num.setter
    @setter
    def num(self: Self, value: SupportsIndex, /) -> None:
        """Validate and assign the qualifier number."""
        number: int
        number = operator.index(value)
        if number < 0:
            raise ValueError
        if number and not self.lit:
            self.string = number
        else:
            self._num = number
