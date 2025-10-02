from __future__ import annotations

import string as string_
from typing import *

from v440._utils.Cfg import Cfg


# parse_pre
def parse_pre(value: Any) -> tuple:
    v: str = str(value).lower()
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    x: str = v.strip(string_.digits)
    v = v[len(x) :]
    q: bool = x.endswith(".")
    if q:
        if not v:
            raise ValueError
        x = x[:-1]
    p: bool = x.startswith(".")
    if p:
        x = x[1:]
    if x:
        return Cfg.cfg.data["phases"][x], int("0" + v)
    if p or v:
        raise ValueError
    return None, None
