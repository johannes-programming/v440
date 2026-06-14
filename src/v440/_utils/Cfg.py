import enum
import functools
import re
import tomllib
from importlib import resources
from importlib.resources.abc import Traversable
from typing import Any, Self, cast

__all__ = ["Cfg"]


class Cfg(enum.Enum):
    cfg = None

    @functools.cached_property
    def data(self: Self) -> dict[str, Any]:
        "This cached property holds the cfg data."
        file: Traversable
        file = resources.files("v440._utils").joinpath("cfg.toml")
        return tomllib.loads(file.read_text(encoding="utf-8"))

    @classmethod
    def fullmatches(cls: type[Self], key: str, value: str) -> dict[str, str]:
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
    def patterns(self: Self) -> dict[str, re.Pattern[str]]:
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

    @functools.cached_property
    def phases(self: Self) -> dict[str, str]:
        return cast(dict[str, str], Cfg.cfg.data["consts"]["phases"])
