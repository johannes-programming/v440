import enum
import functools
import re


class Pattern(enum.StrEnum):

    EPOCH = r"""(?:(?P<n>[0-9]+)!?)?"""
    PARSER = r"(?:\.?(?P<l>[a-z]+))?(?:\.?(?P<n>[0-9]+))?"
    PUBLIC = r"(v?([0-9]+!)?[0-9]+(\.[0-9]+)*)?"
    QUALIFIERS = r"(([-_\.]?(?P<l>[a-z]+)[-_\.]?(?P<n>[0-9]*))|(-(?P<N>[0-9]+)))"

    @staticmethod
    def compile(value, /):
        return re.compile(value, re.VERBOSE)

    @functools.cached_property
    def bound(self):
        return self.compile(r"^" + self.value + r"$")

    @functools.cached_property
    def leftbound(self):
        return self.compile(r"^" + self.value)

    @functools.cached_property
    def unbound(self):
        return self.compile(self.value)
