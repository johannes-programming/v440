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
    """Model a PEP 440 local-version identifier as normalized segments."""

    __slots__ = ()

    @classmethod
    def _data_parse(
        cls: type[Self], value: list[Any], /
    ) -> tuple[int | str, ...]:
        """Validate and normalize incoming sequence data."""
        return tuple(map(item_parse, value))

    def _deformat(self: Self, body: str, /) -> LocalRestrictor:
        """Infer formatting constraints that reproduce the supplied rendering."""
        if self:
            return LocalRestrictor.by_parts(
                *Cfg.cfg.patterns["local_splitter"].split(body)
            )
        else:
            return LocalRestrictor.by_parts()

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Parse a format specification into normalized rendering fields."""
        literal_flags: str
        magnitude: int
        segment_spec: str
        separator: str
        parts: list[Any]
        split: list[tuple[int, str, str]]
        # Local formatting uses # for numeric width, ^ for forced uppercase, and
        # ~ as a literal-position placeholder; separators are preserved verbatim.
        if spec.strip("#^~.-_"):
            raise ValueError
        parts = Cfg.cfg.patterns["local_splitter"].split(spec) + ["."]
        split = []
        for segment_spec, separator in zip(parts[::2], parts[1::2]):
            literal_flags = segment_spec.lstrip("#")
            if "#" in literal_flags:
                raise ValueError
            magnitude = len(segment_spec) - len(literal_flags)
            if magnitude == 1:
                magnitude = 0
            literal_flags = literal_flags.rstrip("~")
            split.append((magnitude, literal_flags, separator))
        while len(split) and split[-1] == (0, "", "."):
            split.pop()
        return tuple(split)

    def _format_parsed(self: Self, /, *parsed: tuple[Any, ...]) -> str:
        """Render this value from normalized format fields."""
        result: str
        item: int | str
        index: int
        case_flag: str
        character: str
        magnitude: int
        case_flags: str
        separator: str
        result = ""
        for index, item in enumerate(self):
            if index < len(parsed):
                magnitude, case_flags, separator = parsed[index]
            else:
                magnitude, case_flags, separator = 0, "", "."
            if isinstance(item, int):
                result += format(item, f"0{magnitude}d")
                result += separator
                continue
            # Apply case flags only to positions covered by the specification;
            # the remaining literal text keeps its normalized lowercase spelling.
            for case_flag, character in zip(case_flags, item):
                result += character.upper() if case_flag == "^" else character
            result += item[len(case_flags) :]
            result += separator
        result = result[:-1]
        return result

    @classmethod
    def _sort(cls: type[Self], value: Any, /) -> tuple[bool, int | str]:
        """Return the comparison key for one normalized sequence item."""
        return type(value) is int, value

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
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
        """Return the packaging-compatible representation of this value."""
        if self:
            return str(self)
        else:
            return None

    @packaging.setter
    @setter
    def packaging(self: Self, value: Any, /) -> None:
        """Update this value from its packaging-compatible representation."""
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
    """Normalize one local-version segment to an integer or lowercase text."""
    parsed_item: int | str
    try:
        parsed_item = operator.index(value)
    except Exception:
        parsed_item = str(value).lower()
        if parsed_item.strip(string_.digits + string_.ascii_lowercase):
            raise
        if not parsed_item.strip(string_.digits):
            parsed_item = int(parsed_item)
    else:
        if parsed_item < 0:
            raise ValueError
    return parsed_item


def sort_key(item: int | str, /) -> tuple[bool, int | str]:
    "Return key for sorting int before str in Local."
    return isinstance(item, int), item
