from __future__ import annotations

from typing import *

from v440._utils.Pattern import Pattern
from v440._utils.qualparse import segmenting
from v440._utils.qualparse.Digest import Digest

parse_dev: Digest = Digest("parse_dev")


@parse_dev.overload()
def parse_dev() -> None:
    return


@parse_dev.overload(int)
def parse_dev(value: int) -> int:
    if value < 0:
        raise ValueError
    return value


@parse_dev.overload(list)
def parse_dev(value: list) -> Optional[int]:
    x: Any
    y: Any
    x, y = map(segmenting.segment, value)
    if x != "dev":
        raise ValueError
    if isinstance(y, str):
        raise TypeError
    return y


@parse_dev.overload(str)
def parse_dev(value: str) -> Optional[int]:
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    x: Any
    y: Any
    x, y = m.groups()
    if x not in (None, "dev"):
        raise ValueError
    if y is not None:
        return int(y)
