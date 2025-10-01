from __future__ import annotations

from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Pattern import Pattern
from v440._utils.qualparse import segmenting
from v440._utils.qualparse.Digest import Digest

parse_pre: Digest = Digest("parse_pre")


@parse_pre.overload(list)
def parse_pre(value: list) -> tuple:
    x: Any
    y: Any
    x, y = map(segmenting.segment, value)
    if (x, y) == (None, None):
        return None, None
    x = Cfg.cfg.data["phases"][x]
    if not isinstance(y, int):
        raise TypeError
    return x, y


@parse_pre.overload(str)
def parse_pre(value: str) -> tuple:
    if value == "":
        return [None, None]
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = Cfg.cfg.data["phases"][l]
    n = 0 if (n is None) else int(n)
    return l, n
