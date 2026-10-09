"""Provide configuration and pattern utilities for v440."""

from __future__ import annotations

__all__: list[str] = ["Cfg"]

import enum
import functools
import re
import string as string_
import tomllib
from importlib import resources
from importlib.resources.abc import Traversable
from typing import Any, Self


class Cfg(enum.Enum):
    """Expose parsed configuration data and compiled grammar patterns."""

    cfg = None

    @functools.cached_property
    def data(self: Self, /) -> dict[str, Any]:
        """Return the cached configuration data."""
        file: Traversable
        file = resources.files("v440._utils").joinpath("cfg.toml")
        return tomllib.loads(file.read_text(encoding="utf-8"))

    @classmethod
    def fullmatches(
        cls: type[Self], /, key: str, value: str
    ) -> dict[str, str]:
        """Match a configured pattern against the entire value and normalize missing groups to empty strings."""
        ans: dict[Any, Any]
        fullmatch: Any
        group_name: str
        fullmatch = cls.cfg.patterns[key].fullmatch(value)
        ans = fullmatch.groupdict()
        for group_name in ans.keys():
            if ans[group_name] is None:
                ans[group_name] = ""
        return ans

    @functools.cached_property
    def local_trans(self: Self, /) -> dict[int, int]:
        source_chars: str
        target_chars: str
        source_chars = string_.ascii_uppercase
        target_chars = "^" * len(string_.ascii_uppercase)
        source_chars += string_.ascii_lowercase
        target_chars += "~" * len(string_.ascii_lowercase)
        source_chars += string_.digits
        target_chars += "#" * len(string_.digits)
        return str.maketrans(source_chars, target_chars)

    @functools.cached_property
    def patterns(self: Self, /) -> dict[str, re.Pattern[str]]:
        """Compile the configured grammar fragments into named regular-expression patterns."""
        ans: dict[str, re.Pattern[str]]
        parts: dict[str, str]
        name: str
        template: str
        pattern: str
        ans = dict()
        parts = dict()
        for name, template in self.data["patterns"].items():
            pattern = template.format(**parts)
            parts[name] = f"(?P<{name}>{pattern})"
            ans[name] = re.compile(
                pattern, re.ASCII | re.IGNORECASE | re.VERBOSE
            )
        return ans
