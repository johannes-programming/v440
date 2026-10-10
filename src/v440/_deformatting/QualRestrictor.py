"""Restrict qualifier segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["QualRestrictor"]

from dataclasses import dataclass
from itertools import product
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

    def best(self: Self, /) -> str:
        """Return the shortest qualifier format satisfying every observation.

        A blank fragment selects a qualifier's canonical formatting, rather
        than suppressing that qualifier.  Also, a separator between two
        unnumbered qualifiers may belong to either fragment.  Check the
        complete format grammar after combining the admissible fragments.
        """
        candidates: set[str] = set()
        brackets: QualRow[tuple[str, str]]
        fragments: tuple[tuple[str, ...], ...]
        matches: dict[str, str]
        spec: str
        for brackets in self.bracket_rows:
            fragments = tuple(
                self._options(index, brackets[index]) for index in range(5)
            )
            for parts in product(*fragments):
                spec = "".join(parts)
                try:
                    matches = Cfg.fullmatches("qual_f", spec)
                except (AttributeError, ValueError):
                    continue
                if self._valid(matches):
                    candidates.add(spec)
        if not candidates:
            raise ValueError("No qualifier format satisfies these constraints")
        return min(candidates, key=lambda item: (len(item), item))

    def _options(
        self: Self, index: int, bracket: tuple[str, str], /
    ) -> tuple[str, ...]:
        """List possible formats for a field, including canonical shorthand."""
        lit = self.lit_row[index]
        mag = self.mag_row[index]
        if not lit:
            name = ("a", "b", "rc", "post", "dev")[index]
            return tuple(Cfg.cfg.data["qual-restrictor"]["inactive"][name])
        head = bracket[0] + lit + bracket[1]
        widths = (-mag,) if mag < 0 else ((0,) if mag == 0 else (0, 1))
        options = {head + "#" * width for width in widths}
        if index == 3 and lit == "-" and mag == -1:
            options.add("-")
        if mag > 0 or mag == -1:
            if (
                index < 3
                and bracket == ("", "")
                and lit == ("a", "b", "rc")[index]
            ):
                options.add("")
            elif index == 3 and bracket == (".", "") and lit == "post":
                options.add("")
            elif index == 4 and bracket == (".", "") and lit == "dev":
                options.add("")
        return tuple(sorted(options, key=lambda item: (len(item), item)))

    def _valid(self: Self, matches: dict[str, str], /) -> bool:
        """Check parsed fragments against one coherent separator assignment."""
        names = ("a", "b", "rc", "post", "dev")
        actual_brackets: list[tuple[str, str]] = []
        for index, name in enumerate(names):
            expected_lit = self.lit_row[index]
            expected_mag = self.mag_row[index]
            fragment = matches[f"{name}_f"]
            if not expected_lit:
                actual_brackets.append(("", ""))
                continue
            if not fragment:
                canonical = (expected_mag > 0 or expected_mag == -1) and (
                    (index < 3 and expected_lit == name)
                    or (index == 3 and expected_lit == "post")
                    or (index == 4 and expected_lit == "dev")
                )
                if not canonical:
                    return False
                actual_brackets.append((".", "") if index >= 3 else ("", ""))
                continue
            if index == 3 and matches["post_hyphen_f"]:
                actual_lit = "-"
                bracket = ("", "")
                width = len(matches["post_num_f"])
            else:
                actual_lit = matches[f"{name}_lit"]
                bracket = (
                    matches[f"{name}_prefix"],
                    matches[f"{name}_suffix"],
                )
                width = len(matches[f"{name}_num_f"])
            if actual_lit != expected_lit:
                return False
            if expected_mag < 0 and width != -expected_mag:
                # The implicit hyphen form always emits at least one digit:
                # format(Post(0), "-") is "-0" even with no '#' characters.
                if not (
                    index == 3
                    and actual_lit == "-"
                    and width == 0
                    and expected_mag == -1
                ):
                    return False
            if expected_mag == 0 and width != 0:
                return False
            if expected_mag > 0 and width > expected_mag:
                return False
            actual_brackets.append(bracket)
        return QualRow(*actual_brackets) in self.bracket_rows

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
            if (
                i == -1
                or (not bracket_row_[i][1])
                or mag_row_[i]
                or bracket_row_[j][0]
            ):
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

    def union(self: Self, other: Self, /) -> Self:
        """Combine compatible constraints, retaining separator ambiguities."""
        literals: list[str] = []
        magnitudes: list[int] = []
        for index in range(5):
            left_lit, right_lit = self.lit_row[index], other.lit_row[index]
            if left_lit and right_lit and left_lit != right_lit:
                raise ArithmeticError("Incompatible qualifier spellings")
            literals.append(left_lit or right_lit)
            if not left_lit:
                magnitudes.append(other.mag_row[index])
            elif not right_lit:
                magnitudes.append(self.mag_row[index])
            else:
                left, right = self.mag_row[index], other.mag_row[index]
                if left < 0:
                    if right == 0 or (right < 0 and left != right):
                        raise ArithmeticError("Incompatible qualifier widths")
                    if right > 0 and -left > right:
                        raise ArithmeticError("Incompatible qualifier widths")
                    magnitudes.append(left)
                elif right < 0:
                    if left == 0 or -right > left:
                        raise ArithmeticError("Incompatible qualifier widths")
                    magnitudes.append(right)
                else:
                    magnitudes.append(min(left, right))

        brackets: set[QualRow[tuple[str, str]]] = set()
        for left_row, right_row in product(
            self.bracket_rows, other.bracket_rows
        ):
            combined: list[tuple[str, str]] = []
            for index in range(5):
                if (
                    self.lit_row[index]
                    and other.lit_row[index]
                    and left_row[index] != right_row[index]
                ):
                    break
                combined.append(
                    left_row[index]
                    if self.lit_row[index]
                    else right_row[index]
                )
            else:
                brackets.add(QualRow(*combined))
        if not brackets:
            raise ArithmeticError("Incompatible qualifier separators")
        return type(self)(
            lit_row=QualRow(*literals),
            mag_row=QualRow(*magnitudes),
            bracket_rows=frozenset(brackets),
        )


def to_mag(text: str, /) -> int:
    if text.startswith("0"):
        return -len(text)
    else:
        return len(text)
