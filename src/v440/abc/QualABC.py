"""Provide the QualABC abstract base for qualified v440 classes."""

__all__ = ["QualABC"]

import operator
import string as string_
from abc import abstractmethod
from typing import Any, Self, SupportsIndex

from v440.abc.NestedABC import NestedABC


class QualABC(NestedABC):
    _lit: str
    _num: int
    __slots__ = ("_lit", "_num")

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @classmethod
    def _init_factories(cls: type[Self]) -> dict[str, Any]:
        return dict(_lit=str, _num=int)

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type[Self], value: str) -> str: ...

    def _string_fset(self: Self, value: str) -> None:
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
            if not y:
                raise ValueError
        if x.startswith("."):
            x = x[1:]
        if not x:
            raise ValueError
        self._lit = self._lit_parse(x)
        self._num = int("0" + y)

    def _todict(self: Self) -> dict[str, Any]:
        return dict(lit=self.lit, num=self.num)

    @property
    def lit(self: Self) -> str:
        return self._lit

    @lit.setter
    def lit(self: Self, value: object) -> None:
        x: str
        x = str(value).lower()
        if x:
            self._lit = self._lit_parse(x)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""

    @property
    def num(self: Self) -> int:
        return self._num

    @num.setter
    def num(self: Self, value: SupportsIndex) -> None:
        y: int
        y = operator.index(value)
        if y < 0:
            raise ValueError
        if y and not self.lit:
            self.string = y
        else:
            self._num = y
