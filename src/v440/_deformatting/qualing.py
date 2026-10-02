from __future__ import annotations

__all__: list[str] = ["QualAccumulation"]

import re
from dataclasses import dataclass
from typing import ClassVar, NamedTuple, Self


class QualRow(NamedTuple):
    a: str
    b: str
    rc: str
    post: str
    dev: str


@dataclass(frozen=True, kw_only=True)
class QualInfo:
    num_row: QualRow
    lit_rows: frozenset[QualRow]

    _ABSENT: ClassVar[str] = "?"
    _SEP: ClassVar[tuple[str, ...]] = ("", ".", "-", "_")
    _PRE_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "a": ("alpha", "a"),
        "b": ("beta", "b"),
        "rc": ("preview", "pre", "c", "rc"),
    }
    _POST_ALIASES: ClassVar[tuple[str, ...]] = ("post", "rev", "r")

    # This is the qualifier-only tail of the permissive PEP 440 reference
    # pattern.  Keeping the same alternative order and greedy optionals is
    # important: it defines which numeric interpretation wins for strings
    # that the grammar can otherwise segment in more than one way.
    _QUAL_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"""
        (?P<pre>
            [-_.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_.]?
                (?P<post_l>post|rev|r)
                [-_.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>
            [-_.]?
            (?P<dev_l>dev)
            [-_.]?
            (?P<dev_n>[0-9]+)?
        )?
        \Z
        """,
        re.ASCII | re.IGNORECASE | re.VERBOSE,
    )

    @classmethod
    def by_string(cls, text: str, /) -> Self:
        """Parse *text* as a PEP 440 qual, preserving all literal splits.

        ``num_row`` follows the parsing precedence of PEP 440's reference
        regular expression.  ``lit_rows`` then contains every grammar-valid
        literal segmentation that has exactly that same numeric row.
        """
        match = cls._QUAL_RE.fullmatch(text)
        if match is None:
            raise ValueError(f"not a PEP 440-conforming qual: {text!r}")

        num_row = cls._num_row_from_match(match)
        lit_rows = cls._all_literal_rows(text, num_row)

        # A successful reference parse must itself correspond to at least one
        # enumerated segmentation.  Keeping this as an internal assertion
        # catches accidental divergence between the two grammar definitions.
        assert lit_rows

        return cls(num_row=num_row, lit_rows=frozenset(lit_rows))

    @classmethod
    def _num_row_from_match(cls, match: re.Match[str]) -> QualRow:
        values = [cls._ABSENT] * 5

        pre_l = match.group("pre_l")
        if pre_l is not None:
            pre_l = pre_l.lower()
            if pre_l in {"alpha", "a"}:
                index = 0
            elif pre_l in {"beta", "b"}:
                index = 1
            else:
                index = 2
            values[index] = match.group("pre_n") or ""

        if match.group("post") is not None:
            post_n1 = match.group("post_n1")
            post_n2 = match.group("post_n2")
            values[3] = post_n1 if post_n1 is not None else (post_n2 or "")

        if match.group("dev") is not None:
            values[4] = match.group("dev_n") or ""

        return QualRow(*values)

    @classmethod
    def _literal_forms(cls, field: str, num: str) -> tuple[str, ...]:
        """Return every lowercase literal prefix allowed for one segment."""
        forms: set[str] = set()

        if field in cls._PRE_ALIASES:
            for before in cls._SEP:
                for alias in cls._PRE_ALIASES[field]:
                    for after in cls._SEP:
                        forms.add(before + alias + after)

        elif field == "post":
            # Implicit post-release spelling: ``-N``.  Unlike the explicit
            # spellings, it cannot use an implicit numeric value.
            if num:
                forms.add("-")
            for before in cls._SEP:
                for alias in cls._POST_ALIASES:
                    for after in cls._SEP:
                        forms.add(before + alias + after)

        elif field == "dev":
            for before in cls._SEP:
                for after in cls._SEP:
                    forms.add(before + "dev" + after)

        else:  # pragma: no cover - private misuse guard
            raise AssertionError(field)

        # Longest-first is not semantically necessary, but it tends to find
        # the reference-regex-like split first and makes debugging friendlier.
        return tuple(sorted(forms, key=lambda item: (-len(item), item)))

    @classmethod
    def _all_literal_rows(cls, text: str, num_row: QualRow) -> set[QualRow]:
        fields = QualRow._fields
        present = [
            (index, field, num)
            for index, (field, num) in enumerate(zip(fields, num_row))
            if num != cls._ABSENT
        ]

        rows: set[QualRow] = set()
        base = [cls._ABSENT] * 5

        def visit(which: int, pos: int, row: list[str]) -> None:
            if which == len(present):
                if pos == len(text):
                    rows.add(QualRow(*row))
                return

            index, field, num = present[which]
            for literal_pattern in cls._literal_forms(field, num):
                end = pos + len(literal_pattern) + len(num)
                if end > len(text):
                    continue

                literal = text[pos : pos + len(literal_pattern)]
                digits = text[pos + len(literal_pattern) : end]

                if literal.lower() != literal_pattern:
                    continue
                if digits != num:
                    continue

                next_row = row.copy()
                next_row[index] = literal
                visit(which + 1, end, next_row)

        visit(0, 0, base)
        return rows


def lit_row_union(rowA: QualRow, rowB: QualRow) -> set[QualRow]:
    ans = list()
    for a, b in zip(rowA, rowB):
        if a == "?":
            ans.append(b)
        elif b == "?":
            ans.append(a)
        elif a == b:
            ans.append(a)
        else:
            return set()
    return {QualRow(*ans)}


@dataclass(frozen=True, kw_only=True)
class QualAccumulation:
    mag_row: tuple[int | None, int | None, int | None, int | None, int | None]
    lit_rows: frozenset[QualRow]

    def best(self: Self, /) -> str:
        pass

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        qual_info = QualInfo.by_string(text)
        mag_row = list()
        for num in qual_info.mag_row:
            if num == "?":
                mag_row.append(None)
            elif num.startswith("0"):
                mag_row.append(len(num))
            else:
                mag_row.append(-len(num))
        return cls(mag_row=tuple(mag_row), lit_rows=qual_info.lit_rows)

    def union(self: Self, other: Self, /) -> Self:
        mag_row = list()
        for a, b in zip(self.mag_row, other.mag_row):
            if a is None:
                mag_row.append(b)
            elif b is None:
                mag_row.append(a)
            elif a + b <= 0:
                mag_row.append(max(a, b))
            else:
                raise ValueError
        lit_rows = set()
        for rowA in self.lit_rows:
            for rowB in other.lit_rows:
                lit_rows.update(lit_row_union(rowA, rowB))
        return type(self)(mag_row=tuple(mag_row), lit_rows=frozenset(lit_rows))
