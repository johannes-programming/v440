from __future__ import annotations

import functools
import operator
import string
import types
from typing import *

import setdoc

from v440._utils.Cfg import Cfg
from v440._utils.Pattern import Pattern
from v440.core.VersionError import VersionError


# parse_pre
def parse_pre(value: Any) -> tuple:
    v: str = str(value).lower()
    if v == "":
        return None, None
    v = v.replace("_", ".")
    v = v.replace("-", ".")
    m: Any = Pattern.PARSER.bound.search(v)
    l: Any
    n: Any
    l, n = m.groups()
    l = Cfg.cfg.data["phases"][l]
    n = 0 if (n is None) else int(n)
    return l, n
