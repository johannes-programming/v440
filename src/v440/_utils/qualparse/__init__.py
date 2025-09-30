from __future__ import annotations

from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.qualparse import segmenting

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


parse_pre: Digest = Digest("parse_pre")


@parse_pre.overload()
def parse_pre() -> tuple:
    return None, None


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
