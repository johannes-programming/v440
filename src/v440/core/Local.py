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
    """Store normalized local-version identifier components."""

    __slots__ = ()

    @classmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> tuple[int | str, ...]:
        """Normalize local-version sequence items."""
        return tuple(map(item_parse, value))

    def _deformat(self: Self, body: str, /) -> LocalRestrictor:
        """Infer formatting constraints from one local-version rendering."""
        if self:
            return LocalRestrictor.by_parts(
                *Cfg.cfg.patterns["local_splitter"].split(body)
            )
        else:
            return LocalRestrictor.by_parts()

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Parse a local-version format specification into per-segment formatting constraints."""
        literal_pattern: str
        magnitude: int
        item_spec: str
        separator: str
        parts: list[Any]
        split: list[tuple[int, str, str]]
        if spec.strip("#^~.-_"):
            raise ValueError
        parts = Cfg.cfg.patterns["local_splitter"].split(spec) + ["."]
        split = []
        for item_spec, separator in zip(parts[::2], parts[1::2]):
            literal_pattern = item_spec.lstrip("#")
            if "#" in literal_pattern:
                raise ValueError
            magnitude = len(item_spec) - len(literal_pattern)
            if magnitude == 1:
                magnitude = 0
            literal_pattern = literal_pattern.rstrip("~")
            split.append((magnitude, literal_pattern, separator))
        while len(split) and split[-1] == (0, "", "."):
            split.pop()
        return tuple(split)

    def _format_parsed(self: Self, /, *parsed: tuple[Any, ...]) -> str:
        """Render local-version segments from parsed width, case, and separator constraints."""
        ans: str
        item: int | str
        index: int
        case_marker: str
        character: str
        magnitude: int
        literal_pattern: str
        separator: str
        ans = ""
        for index, item in enumerate(self):
            if index < len(parsed):
                magnitude, literal_pattern, separator = parsed[index]
            else:
                magnitude, literal_pattern, separator = 0, "", "."
            if isinstance(item, int):
                ans += format(item, f"0{magnitude}d")
                ans += separator
                continue
            for case_marker, character in zip(literal_pattern, item):
                ans += character.upper() if case_marker == "^" else character
            ans += item[len(literal_pattern) :]
            ans += separator
        ans = ans[:-1]
        return ans

    @classmethod
    def _sort(cls: type[Self], value: Any, /) -> tuple[bool, int | str]:
        """Return the comparison key for one local-version component."""
        return type(value) is int, value

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse and normalize a local-version identifier string."""
        normalized: str
        if value == "":
            self.data = ()
            return
        normalized = value
        if normalized.startswith("+"):
            normalized = normalized[1:]
        normalized = normalized.replace("_", ".")
        normalized = normalized.replace("-", ".")
        self.data = normalized.split(".")

    @property
    def packaging(self: Self, /) -> str | None:
        """Return the local identifier in packaging-compatible form."""
        if self:
            return str(self)
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: Any, /) -> None:
        """Replace the local identifier from a packaging-compatible value."""
        if value is None:
            self.string = ""
        else:
            self.string = value

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        """Sort local-version components using PEP 440 ordering by default."""
        self.data = sorted(
            self,
            key=sort_key if key is None else key,
            reverse=reverse,
        )


def item_parse(value: Any, /) -> int | str:
    """Normalize one local-version component as a nonnegative integer or lowercase string."""
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
    """Return key for sorting int before str in Local."""
    return isinstance(item, int), item
