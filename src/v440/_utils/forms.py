import string as string_
from typing import *


def none_empty(groupdict: dict, key: str) -> Any:
    if groupdict[key] is None:
        return ""
    else:
        return groupdict[key]


def qualdeform(*strings: str) -> str:
    a: str = ""
    f: int = -1
    u: int = -1
    s: str
    x: str
    y: str
    for s in strings:
        if s == "":
            continue
        x = s.rstrip(string_.digits)
        if a == "":
            a = x
        elif a != x:
            raise ValueError
        y = s[len(x) :]
        if u == -1 or u > len(y):
            u = len(y)
        if not y.startswith("0"):
            continue
        if y == "0" and x[-1] in ".-_":
            continue
        if f == -1:
            f = len(y)
            continue
        if f != len(y):
            raise ValueError
    if f > u:
        raise ValueError
    if f == -1:
        f = 0
    a += "#" * f
    return a


def qualform(mask: str, num: int) -> str:
    x: str = mask.rstrip("#")
    n: int = len(mask) - len(x)
    if n or (x[-1:] in tuple(".-_")):
        x += format(num, f"0{n}d")
    return x
