import enum
import functools
import re
from typing import *

class Pattern(enum.StrEnum):

    EPOCH = r"""(?:(?P<n>[0-9]+)!?)?"""
    PARSER = r"(?:\.?(?P<l>[a-z]+))?(?:\.?(?P<n>[0-9]+))?"
    PUBLIC = r"(v?([0-9]+!)?[0-9]+(\.[0-9]+)*)?"
    QUALIFIERS = r"(([-_\.]?(?P<l>[a-z]+)[-_\.]?(?P<n>[0-9]*))|(-(?P<N>[0-9]+)))"

    @staticmethod
    def compile(value:Any, /)->Any:
        return re.compile(value, re.VERBOSE)

    @functools.cached_property
    def bound(self:Self)->Any:
        return self.compile(r"^" + self.value + r"$")

    @functools.cached_property
    def leftbound(self:Self)->Any:
        return self.compile(r"^" + self.value)

    @functools.cached_property
    def unbound(self:Self)->Any:
        return self.compile(self.value)
