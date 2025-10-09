from typing import *
import string as string_
import operator
from v440.core.VersionError import VersionError

__all__ = ["to_numeral", "to_segment"]

SEGCHARS:str = string_.digits + string_.ascii_lowercase

def to_numeral(value:Any) -> int:
    try:
        return to_numeral_(value)
    except Exception:
        pass
    raise VersionError("%r is not a valid numeral." % value)

def to_numeral_(value:Any) -> int:
    ans:int = operator.index(value)
    if ans < 0:
        raise Exception
    return ans

def to_segment(value:Any) -> int | str:
    try:
        return to_segment_(value)
    except Exception:
        pass
    raise VersionError("%r is not a valid segment." % value)

def to_segment_(value:Any) -> int|str:
    ans:Optional[int|str] = None
    try:
        ans = operator.index(value)
    except Exception:
        ans = str(value).lower()
        if ans.strip(SEGCHARS):
            raise Exception
        if not ans.strip(string_.digits):
            ans = int(ans)
    else:
        if ans < 0:
            raise Exception
    return ans

