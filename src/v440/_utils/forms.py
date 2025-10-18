from typing import *


def none_empty(groupdict: dict, key: str) -> Any:
    if groupdict[key] is None:
        return ""
    else:
        return groupdict[key]


def qualform(mask: str, num: int) -> str:
    x: str = mask.rstrip("#")
    n: int = len(mask) - len(x)
    x += format(num, f"0{n}d")
    return x
