"""Provide configuration and pattern utilities for v440."""

from __future__ import annotations

__all__: list[str] = ["Cfg"]

import enum
import functools
import re
import tomllib
from importlib import resources
from importlib.resources.abc import Traversable
from typing import Any, Self, cast


class Cfg(enum.Enum):
    """Load v440 configuration data and compile its regular-expression patterns."""

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
        """Match a configured pattern and normalize missing groups to empty strings."""
        groups: dict[Any, Any]
        fullmatch: Any
        group_name: str
        fullmatch = cls.cfg.patterns[key].fullmatch(value)
        groups = fullmatch.groupdict()
        for group_name in groups.keys():
            if groups[group_name] is None:
                groups[group_name] = ""
        return groups

    @functools.cached_property
    def patterns(self: Self, /) -> dict[str, re.Pattern[str]]:
        """Compile configured regular-expression fragments in dependency order."""
        patterns: dict[str, re.Pattern[str]]
        named_parts: dict[str, str]
        name: str
        template: str
        expanded: str
        patterns = dict()
        named_parts = dict()
        for name, template in self.data["patterns"].items():
            expanded = template.format(**named_parts)
            named_parts[name] = f"(?P<{name}>{expanded})"
            patterns[name] = re.compile(expanded, re.IGNORECASE | re.VERBOSE)
        return patterns
