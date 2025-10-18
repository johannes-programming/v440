import enum
import functools
import re
import tomllib
from importlib import resources
from typing import *

__all__ = ["Cfg"]


class Cfg(enum.Enum):
    cfg = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("v440._utils", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans

    @classmethod
    def none_empty(cls: type, value: Any) -> Any:
        if value is None:
            return ""
        else:
            return value

    @functools.cached_property
    def patterns(self: Self) -> dict[str, re.Pattern]:
        ans: dict = dict()
        parts: dict = dict()
        x: str
        y: str
        z: str
        for x, y in self.data["patterns"].items():
            z = y.format(**parts)
            ans[x] = re.compile(z, re.VERBOSE | re.IGNORECASE)
            parts[x] = y
        return ans
