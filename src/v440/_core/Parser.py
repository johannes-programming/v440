from __future__ import annotations

import dataclasses
import functools
import re

from overloadable import overloadable

from v440._core import utils
from v440._core.Pattern import Pattern


@dataclasses.dataclass(frozen=True)
class Parser:
    keysforlist: tuple = None
    keysforstr: tuple = None
    phasedict: dict = None
    allow_len_1: bool = False

    @functools.cached_property
    def dual(self):
        return type(self.phasedict) is dict

    def nbylist(self, value, /):
        if len(value) == 2:
            l, n = value
            if l not in self.keysforlist:
                raise ValueError
            return n
        if len(value) == 1:
            n = value[0]
            if not self.allow_len_1:
                raise ValueError
            return n
        raise ValueError

    @overloadable
    def parse(self, value, /):
        if value is None:
            return "del"
        if isinstance(value, int):
            return "int"
        if isinstance(value, str):
            return "str"
        if hasattr(value, "__iter__"):
            return "list"
        return "str"

    @parse.overload("del")
    def parse(self, value, /):
        return [None, None] if self.dual else None

    @parse.overload("int")
    def parse(self, value, /):
        if self.dual:
            raise TypeError
        value = int(value)
        if value < 0:
            raise ValueError
        return value

    @parse.overload("list")
    def parse(self, value, /):
        value = [utils.segment(x) for x in value]
        if self.dual:
            l, n = value
            if [l, n] == [None, None]:
                return [None, None]
            l = self.phasedict[l]
            if not isinstance(n, int):
                raise TypeError
            return [l, n]
        else:
            n = self.nbylist(value)
            if isinstance(n, str):
                raise TypeError
            return n

    @parse.overload("str")
    def parse(self, value, /):
        value = str(value).lower().strip()
        value = value.replace("_", ".")
        value = value.replace("-", ".")
        if self.dual and value == "":
            return [None, None]
        l, n = Pattern.PARSER.bound.fullmatch(value).groups()
        if self.dual:
            l = self.phasedict[l]
            n = 0 if (n is None) else int(n)
            return [l, n]
        if l not in self.keysforstr:
            raise ValueError
        if n is None:
            return None
        else:
            return int(n)


POST = Parser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
DEV = Parser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)
PRE = Parser(
    phasedict=dict(
        alpha="a",
        a="a",
        beta="b",
        b="b",
        preview="rc",
        pre="rc",
        c="rc",
        rc="rc",
    ),
)
