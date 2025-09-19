from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern

__all__ = ["SimpleQualifierParser"]


class SimpleQualifierParser:
    __slots__ = ("_keysforlist", "_keysforstr", "_allow_len_1")

    __call__ = Digest("__call__")

    @__call__.overload()
    def __call__(self: Self) -> Optional[list]:
        pass

    @__call__.overload(int)
    def __call__(self: Self, value: int) -> Any:
        if value < 0:
            raise ValueError
        return value

    @__call__.overload(list)
    def __call__(self: Self, value: list) -> Any:
        v: list = list(map(utils.segment, value))
        n: Any = self.nbylist(v)
        if isinstance(n, str):
            raise TypeError
        return n

    @__call__.overload(str)
    def __call__(self: Self, value: str) -> Optional[int | list]:
        v: str = value
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        m: Any = Pattern.PARSER.bound.search(v)
        x: Any
        y: Any
        x, y = m.groups()
        if x not in self.keysforstr:
            raise ValueError
        if y is None:
            return None
        else:
            return int(y)

    def __init__(
        self: Self,
        keysforlist: Iterable = (),
        keysforstr: Iterable = (),
        allow_len_1: Any = False,
    ) -> None:
        self._keysforlist = tuple(map(str, keysforlist))
        self._keysforstr = tuple(map(self.optstr, keysforstr))
        self._allow_len_1 = bool(allow_len_1)

    @property
    def allow_len_1(self: Self) -> tuple:
        return self._allow_len_1

    @property
    def keysforlist(self: Self) -> tuple:
        return self._keysforlist

    @property
    def keysforstr(self: Self) -> tuple:
        return self._keysforstr

    def nbylist(self: Self, value: Any, /) -> Any:
        if len(value) == 2:
            if value[0] in self.keysforlist:
                return value[1]
        if len(value) == 1:
            if self.allow_len_1:
                return value[0]
        raise ValueError

    @classmethod
    def optstr(cls: type, value: Any) -> Optional[str]:
        if value is None:
            return
        else:
            return str(value)


POST: SimpleQualifierParser = SimpleQualifierParser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
DEV: SimpleQualifierParser = SimpleQualifierParser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)
