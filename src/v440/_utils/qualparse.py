from __future__ import annotations

from typing import *

from v440._utils import utils
from v440._utils.Cfg import Cfg
from v440._utils.Digest import Digest
from v440._utils.Pattern import Pattern
from v440._utils.SimpleQualifierParser import SimpleQualifierParser

parse_leg: Digest = Digest("parse_leg")


@parse_leg.overload()
def parse_leg() -> list:
    return [None, None, None]


@parse_leg.overload(int)
def parse_leg(value: int) -> list:
    return [None, abs(value), None]


@parse_leg.overload(list)
def parse_leg(value: list) -> list:
    return [value[:2]] + value[2:]


@parse_leg.overload(str)
def parse_leg(value: str) -> list:
    v = value
    prephase: Any = None
    presubphase: Any = None
    post: Any = None
    dev: Any = None
    m: Any
    x: Any
    y: Any
    while v:
        m = Pattern.QUALIFIERS.leftbound.search(v)
        v = v[m.end() :]
        if m.group("N"):
            post = m.group("N")
            continue
        x = m.group("l")
        y = m.group("n")
        if x == "dev":
            dev = y
            continue
        if x in ("post", "r", "rev"):
            post = y
            continue
        prephase = x
        presubphase = y
    return [[prephase, presubphase], post, dev]


parse_pre: Digest = Digest("parse_pre")


@parse_pre.overload()
def parse_pre() -> list:
    return [None, None]


@parse_pre.overload(list)
def parse_pre(value: list) -> Any:
    l: Any
    n: Any
    l, n = list(map(utils.segment, value))
    if [l, n] == [None, None]:
        return [None, None]
    l = Cfg.cfg.data["phases"][l]
    if not isinstance(n, int):
        raise TypeError
    return [l, n]


@parse_pre.overload(str)
def parse_pre(value: str) -> list:
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
    return [l, n]


parse_dev: SimpleQualifierParser = SimpleQualifierParser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)

parse_post: SimpleQualifierParser = SimpleQualifierParser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
