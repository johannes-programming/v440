import string as string_
from typing import *


def qualdeform(*strings: str, hollow: str) -> str:
    lits: set = set()
    nums: set = set()
    for s in strings:
        x = s.rstrip(string_.digits)
        y = s[len(x) :]
        lits.add(x)
        nums.add(y)
    lits.discard("")
    if len(lits) == 0:
        return ""
    (x,) = lits
    u: int = min(map(len, nums))
    f: int = -1
    for y in nums:
        if y.startswith("0"):
            f = max(f, len(y))
    if f > u:
        raise ValueError
    if f == -1:
        f = min(u, int(x == hollow))
    if f == 1 and x == hollow:
        return ""
    if f == 1 and x[-1] in ".-_":
        f = 0
    return x + "#" * f


def qualform(mask: str, num: int) -> str:
    x: str = mask.rstrip("#")
    n: int = len(mask) - len(x)
    if n or num or (x[-1:] in tuple(".-_")):
        x += format(num, f"0{n}d")
    return x
