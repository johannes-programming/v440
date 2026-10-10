"""Restrict qualifier segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["QualRestrictor"]

from collections import abc
from dataclasses import dataclass
from typing import Generic, NamedTuple, Self, TypeVar

from v440._utils.Cfg import Cfg

Item = TypeVar("Item", covariant=True)


class QualRow(NamedTuple, Generic[Item]):
    """Store literal spellings for each qualifier field."""

    a: Item
    b: Item
    rc: Item
    post: Item
    dev: Item


@dataclass(frozen=True, kw_only=True)
class QualRestrictor:
    lit_row: QualRow[str]
    mag_row: QualRow[int]
    bracket_rows: frozenset[QualRow[tuple[str, str]]]

    @classmethod
    def by_string(cls: type[Self], string: str, /) -> Self:
        i: int
        j: int
        lit_row_: list[str]
        mag_row_: list[int]
        matches: dict[str, str]
        bracket_row_: list[tuple[str, str]]
        bracket_rows_: set[QualRow[tuple[str, str]]]
        matches = Cfg.fullmatches("qual", string)
        lit_row_ = list()
        mag_row_ = list()
        bracket_row_ = list()
        for name in ("a", "b", "rc"):
            if matches[f"{name}_lit"]:
                lit_row_.append(matches["pre_lit"])
                mag_row_.append(to_mag(matches["pre_num"]))
                bracket_row_.append(
                    (matches["pre_prefix"], matches["pre_suffix"])
                )
            else:
                lit_row_.append("")
                mag_row_.append(0)
                bracket_row_.append(("", ""))
        if matches["post_impl"]:
            lit_row_.append("-")
            mag_row_.append(to_mag(matches["post_impl_num"]))
            bracket_row_.append(("", ""))
        else:
            lit_row_.append(matches["post_lit"])
            mag_row_.append(to_mag(matches["post_num"]))
            bracket_row_.append(
                (matches["post_prefix"], matches["post_suffix"])
            )
        lit_row_.append(matches["dev_lit"])
        mag_row_.append(to_mag(matches["dev_num"]))
        bracket_row_.append((matches["dev_prefix"], matches["dev_suffix"]))
        bracket_rows_ = {QualRow(*bracket_row_)}
        if matches["post_impl"]:
            return cls(
                lit_row=QualRow(*lit_row_),
                mag_row=QualRow(*mag_row_),
                bracket_rows=frozenset(bracket_rows_),
            )
        i = -1
        for j in range(5):
            if not lit_row_[j]:
                continue
            if i == -1 or (not bracket_row_[i][1]) or bracket_row_[j][0]:
                i = j
                continue
            for bracket_row_ in map(list, frozenset(bracket_rows_)):
                bracket_row_[j] = bracket_row_[i][1], bracket_row_[j][1]
                bracket_row_[i] = bracket_row_[i][0], ""
                bracket_rows_.add(QualRow(*bracket_row_))
            i = j
        return cls(
            lit_row=QualRow(*lit_row_),
            mag_row=QualRow(*mag_row_),
            bracket_rows=frozenset(bracket_rows_),
        )


def to_mag(text: str, /) -> int:
    if text.startswith("0"):
        return -len(text)
    else:
        return len(text)
