from __future__ import annotations

from typing import *

import setdoc

from v440._utils import segmenting
from v440._utils.ListStringer import ListStringer

__all__ = ["Local"]


class Local(ListStringer):
    __slots__ = ()

    string: str
    data: tuple[int | str]

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        ans: tuple = tuple(map(segmenting.segment, value))
        if None in ans:
            raise ValueError
        return ans

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        return ".".join(map(str, self))

    @classmethod
    def _sort(cls: type, value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            return ()
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")
