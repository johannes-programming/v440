import operator
from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr
from overloadable import Overloadable

from v440._utils.BaseStringer import BaseStringer
from v440._utils.Cfg import Cfg
from v440._utils.guarding import guard

__all__ = ["QualStringer"]


class QualStringer(BaseStringer):
    __slots__ = ("_phase", "_num")

    string: str
    phase: str
    num: int

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.phase or self.num)

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> str:
        self._phase = ""
        self._num = 0
        argc: int = len(args) + len(kwargs)
        keys: set = set(kwargs.keys())
        if argc <= 1 and keys <= {"string"}:
            return "string"
        return "slots"

    @__init__.overload("string")
    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self.string = string

    @__init__.overload("slots")
    @setdoc.basic
    def __init__(
        self: Self,
        phase: Any = "",
        num: Any = 0,
    ) -> None:
        self.phase = phase
        self.num = num

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, phase=self.phase, num=self.num)

    def _format(self: Self, format_spec: str) -> str:
        return self._format_cls(
            format_spec=format_spec,
            phase=self.phase,
            num=self.num,
        )

    @classmethod
    @abstractmethod
    def _format_cls(
        cls: type,
        *,
        phase: str,
        num: int,
        format_spec: str = "",
    ) -> str: ...

    @classmethod
    @abstractmethod
    def _name(cls: type) -> str: ...

    @abstractmethod
    def _num_fset(self: Self, value: int) -> None: ...

    @property
    def num(self: Self) -> int:
        return self._num

    @num.setter
    @guard
    def num(self: Self, value: Any) -> None:
        self._num_fset(operator.index(value))

    @property
    def phase(self: Self) -> str:
        return self._phase

    @phase.setter
    @guard
    def phase(self: Self, value: Any) -> None:
        v: str = str(value).lower()
        if v:
            self._phase = Cfg.cfg.data[self._name()][v]
        elif self.num:
            self.string = str(self.num)
        else:
            self._phase = ""
