import enum
import functools
import re
from typing import *

__all__ = ["Pattern"]


class Pattern(enum.StrEnum):

    BASE = r"v?(?:[0-9]+!)?[0-9]+(?:\.[0-9]+)*"
    PRE = r"[-_\.]?(?:alpha|a|beta|b|preview|pre|c|rc)(?:[-_\.]?[0-9]+)?"
    POST = r"(?:-(?:[0-9]+))|(?:(?:[-_\.]?(?:post|rev|r))(?:[-_\.]?(?:[0-9]+))?)"
    DEV = r"[-_\.]?dev(?:[-_\.]?[0-9]+)?"
    QUAL = r"(?P<pre>%s)?(?P<post>%s)?(?P<dev>%s)?" % (PRE, POST, DEV)
    PUBLIC = r"(?P<base>%s)(?P<qual>%s)" % (BASE, QUAL)

    @functools.cached_property
    def bound(self: Self) -> re.Pattern:
        return self.compile(r"^" + self.value + r"$")

    @staticmethod
    def compile(value: Any, /) -> re.Pattern:
        "This staticmethod compiles the given value into a pattern."
        return re.compile(value, re.VERBOSE)

    @functools.cached_property
    def leftbound(self: Self) -> re.Pattern:
        return self.compile(r"^" + self.value)

    @classmethod
    def none_empty(cls: type, value: Optional[str]) -> str:
        if value is None:
            return ""
        else:
            return value

    @classmethod
    def skip(cls: type, value: str, chars: str) -> int:
        i: int = 0
        while i < len(value):
            if value[i] in chars:
                i += 1
            else:
                break
        return i

    @functools.cached_property
    def unbound(self: Self) -> re.Pattern:
        return self.compile(self.value)
