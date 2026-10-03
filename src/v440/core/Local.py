"""Provide the Local class for local version identifiers in v440."""

from __future__ import annotations

__all__: list[str] = ["Local"]

import operator
import string as string_
from typing import Any, Self

from v440._deformatting.LocalRestrictor import LocalRestrictor
from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.abc.ListABC import ListABC


class Local(ListABC[int | str]):
    """Represent Local."""
    __slots__ = ()

    @classmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> tuple[int | str, ...]:
        """Handle data parse."""
        return tuple(map(item_parse, value))

    def _deformat(self: Self, body: str, /) -> LocalRestrictor:
        """Handle deformat."""
        if self:
            return LocalRestrictor.by_parts(
                *Cfg.cfg.patterns["local_splitter"].split(body)
            )
        else:
            return LocalRestrictor.by_parts()

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Handle format parse."""
        l: str
        m: int
        x: str
        y: str
        parts: list[Any]
        split: list[tuple[int, str, str]]
        if spec.strip("#^~.-_"):
            raise ValueError
        parts = Cfg.cfg.patterns["local_splitter"].split(spec) + ["."]
        split = []
        for x, y in zip(parts[::2], parts[1::2]):
            l = x.lstrip("#")
            if "#" in l:
                raise ValueError
            m = len(x) - len(l)
            if m == 1:
                m = 0
            l = l.rstrip("~")
            split.append((m, l, y))
        while len(split) and split[-1] == (0, "", "."):
            split.pop()
        return tuple(split)

    def _format_parsed(self: Self, /, *parsed: tuple[Any, ...]) -> str:
        """Handle format parsed."""
        ans: str
        item: int | str
        index: int
        s: str
        t: str
        x: int
        y: str
        z: str
        ans = ""
        for index, item in enumerate(self):
            if index < len(parsed):
                x, y, z = parsed[index]
            else:
                x, y, z = 0, "", "."
            if isinstance(item, int):
                ans += format(item, f"0{x}d")
                ans += z
                continue
            for s, t in zip(y, item):
                ans += t.upper() if s == "^" else t
            ans += item[len(y) :]
            ans += z
        ans = ans[:-1]
        return ans

    @classmethod
    def _sort(cls: type[Self], value: Any, /) -> tuple[bool, int | str]:
        """Handle sort."""
        return type(value) is int, value

    def _string_fset(self: Self, value: str, /) -> None:
        """Handle string fset."""
        v: str
        if value == "":
            self.data = ()
            return
        v = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    @property
    def packaging(self: Self, /) -> str | None:
        """Perform packaging."""
        if self:
            return str(self)
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: Any, /) -> None:
        """Perform packaging."""
        if value is None:
            self.string = ""
        else:
            self.string = value

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        self.data = sorted(
            self,
            key=sort_key if key is None else key,
            reverse=reverse,
        )


def item_parse(value: Any, /) -> int | str:
    """Perform item parse."""
    ans: int | str
    try:
        ans = operator.index(value)
    except Exception:
        ans = str(value).lower()
        if ans.strip(string_.digits + string_.ascii_lowercase):
            raise
        if not ans.strip(string_.digits):
            ans = int(ans)
    else:
        if ans < 0:
            raise ValueError
    return ans


def sort_key(item: int | str, /) -> tuple[bool, int | str]:
    "Return key for sorting int before str in Local."
    return isinstance(item, int), item
