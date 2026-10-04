"""Provide configuration and pattern utilities for v440."""

__all__: list[str] = ["Cfg"]

import enum
import functools
import re
import string as string_
import tomllib
from importlib import resources
from importlib.resources.abc import Traversable
from typing import Any, Self, cast


class Cfg(enum.Enum):
    """Represent Cfg."""

    cfg = None

    @functools.cached_property
    def data(self: Self, /) -> dict[str, Any]:
        "Return the cached configuration data."
        file: Traversable
        file = resources.files("v440._utils").joinpath("cfg.toml")
        return tomllib.loads(file.read_text(encoding="utf-8"))

    @classmethod
    def fullmatches(
        cls: type[Self], /, key: str, value: str
    ) -> dict[str, str]:
        """Perform fullmatches."""
        ans: dict[Any, Any]
        fullmatch: Any
        x: str
        fullmatch = cls.cfg.patterns[key].fullmatch(value)
        ans = fullmatch.groupdict()
        for x in ans.keys():
            if ans[x] is None:
                ans[x] = ""
        return ans

    @functools.cached_property
    def local_trans(self: Self, /) -> dict[int, int]:
        x: str
        y: str
        x = string_.ascii_uppercase
        y = "^" * len(string_.ascii_uppercase)
        x += string_.ascii_lowercase
        y += "~" * len(string_.ascii_lowercase)
        x += string_.digits
        y += "#" * len(string_.digits)
        return str.maketrans(x, y)

    @functools.cached_property
    def patterns(self: Self, /) -> dict[str, re.Pattern[str]]:
        """Perform patterns."""
        ans: dict[str, re.Pattern[str]]
        parts: dict[str, str]
        x: str
        y: str
        z: str
        ans = dict()
        parts = dict()
        for x, y in self.data["patterns"].items():
            z = y.format(**parts)
            parts[x] = f"(?P<{x}>{z})"
            ans[x] = re.compile(z, re.IGNORECASE | re.VERBOSE)
        return ans
