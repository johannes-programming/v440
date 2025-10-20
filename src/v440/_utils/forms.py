import string as string_
from typing import *


def none_empty(groupdict: dict, key: str) -> Any:
    if groupdict[key] is None:
        return ""
    else:
        return groupdict[key]


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
    u: int = min(1, *map(len, nums))
    nums = set(len(y) for y in nums if y.startswith("0"))
    f: int
    if len(nums):
        (f,) = nums
        if f > u:
            raise ValueError
    elif u == 0 or x[-1] in ".-_":
        f = 0
    else:
        f = 1
    x += f * "#"
    if x == hollow:
        return ""
    else:
        return x


def qualform(mask: str, num: int) -> str:
    x: str = mask.rstrip("#")
    n: int = len(mask) - len(x)
    if n or (x[-1:] in tuple(".-_")):
        x += format(num, f"0{n}d")
    return x
