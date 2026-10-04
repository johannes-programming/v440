"""Provide the QualABC abstract base for qualified v440 classes."""

__all__: list[str] = ["QualABC"]

import operator
import string as string_
from abc import abstractmethod
from typing import Any, Generic, Literal, Self, SupportsIndex, TypeVar

from v440._utils.setter import setter
from v440.abc.NestedABC import NestedABC

Lit = TypeVar("Lit", bound=str)


class QualABC(NestedABC, Generic[Lit]):
    """Represent QualABC."""

    _lit: Lit | Literal[""]
    _num: int
    __slots__ = ("_lit", "_num")

    @abstractmethod
    def _cmp(self: Self, /) -> Any: ...

    @classmethod
    def _init_factories(cls: type[Self], /) -> dict[str, Any]:
        """Handle init factories."""
        return dict(_lit=str, _num=int)

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type[Self], value: str, /) -> Lit: ...

    def _string_fset(self: Self, value: str, /) -> None:
        """Handle string fset."""
        x: str
        y: str
        if value == "":
            self._lit = ""
            self._num = 0
            return
        x = value.rstrip(string_.digits)
        y = value[len(x) :]
        if x == "-":
            if not y:
                raise ValueError
            self._lit = self._lit_parse("-")
            self._num = int(y)
            return
        x = x.replace("-", ".")
        x = x.replace("_", ".")
        if x.endswith("."):
            x = x[:-1]
        if x.startswith("."):
            x = x[1:]
        if not x:
            raise ValueError
        self._lit = self._lit_parse(x)
        self._num = int("0" + y)

    def _todict(self: Self, /) -> dict[str, Any]:
        """Handle todict."""
        return dict(lit=self.lit, num=self.num)

    @property
    def lit(self: Self, /) -> Lit | Literal[""]:
        """Handle lit."""
        return self._lit

    @lit.setter
    @setter
    def lit(self: Self, value: object, /) -> None:
        """Handle lit."""
        x: str
        x = str(value).lower()
        if x:
            self._lit = self._lit_parse(x)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""

    @property
    def num(self: Self, /) -> int:
        """Handle num."""
        return self._num

    @num.setter
    @setter
    def num(self: Self, value: SupportsIndex, /) -> None:
        """Handle num."""
        y: int
        y = operator.index(value)
        if y < 0:
            raise ValueError
        if y and not self.lit:
            self.string = y
        else:
            self._num = y
