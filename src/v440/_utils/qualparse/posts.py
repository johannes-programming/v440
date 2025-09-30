from __future__ import annotations

from typing import *

from v440._utils.Pattern import Pattern
from v440._utils.qualparse import segmenting
from v440._utils.qualparse.Digest import Digest

parse_post: Digest = Digest("parse_post")


@parse_post.overload()
def parse_post() -> None:
    return


@parse_post.overload(int)
def parse_post(value: int) -> int:
    if value < 0:
        raise ValueError
    return value


@parse_post.overload(list)
def parse_post(value: list) -> Optional[int]:
    v: list = list(map(segmenting.segment, value))
    if len(v) == 0:
        raise ValueError
    if len(v) > 2:
        raise ValueError
    if len(v) == 1:
        v.insert(0, "")
    if v[0] not in ("post", "rev", "r", ""):
        raise ValueError
    if isinstance(v[1], str):
        raise TypeError
    return v[1]


@parse_post.overload(str)
def parse_post(value: str) -> Optional[int]:
    v: str = value
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    x: Any
    y: Any
    x, y = m.groups()
    if x not in (None, "post", "rev", "r"):
        raise ValueError
    if y is not None:
        return int(y)
