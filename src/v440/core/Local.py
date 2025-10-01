from __future__ import annotations

import operator
import string as string_
from typing import *

import setdoc
from overloadable import Overloadable

from v440._utils.ListStringer import ListStringer

__all__ = ["Local"]


class Local(ListStringer):
    __slots__ = ()

    string: str
    data: tuple[int | str]

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> bool:
        if "string" in kwargs.keys():
            return True
        if len(args) <= 1 and len(kwargs) == 0:
            return True
        return False

    @__init__.overload(True)
    def __init__(self: Self, string: Any = "") -> None:
        self._data = ()
        self.string = string

    @__init__.overload(False)
    def __init__(self: Self, data: Iterable) -> None:
        self._data = ()
        self.data = data

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        try:
            return tuple(map(cls._item_parse, value))
        except Exception as exc:
            raise ValueError("_dataparse: value=%r" % value)

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        return ".".join(map(str, self))

    @classmethod
    def _item_parse(cls: type, value: Any) -> int | str:
        ans: int | str
        if isinstance(value, int):
            ans = operator.index(value)
            if ans < 0:
                raise ValueError
        else:
            ans = str(value).lower()
            if ans.strip(string_.digits + string_.ascii_lowercase):
                raise ValueError("_item_parse: value=%r" % value)
            if not ans.strip(string_.digits):
                ans = int(ans)
        return ans

    @classmethod
    def _sort(cls: type, value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self.data = ()
            return
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")
