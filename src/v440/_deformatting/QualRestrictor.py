"""Restrict qualifier segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["QualRestrictor"]

import re
from collections import abc
from dataclasses import dataclass
from itertools import product
from typing import ClassVar, NamedTuple, Self

from iterprod import iterprod

from v440._utils.Cfg import Cfg


class QualRow(NamedTuple):
    """Represent QualRow."""
    a: str
    b: str
    rc: str
    post: str
    dev: str


@dataclass(frozen=True, kw_only=True)
class QualInfo:
    """Represent QualInfo."""
    num_row: QualRow
    lit_rows: frozenset[QualRow]

    # This is the qualifier-only tail of the permissive PEP 440 reference
    # pattern.  Keeping the same alternative order and greedy optionals is
    # important: it defines which numeric interpretation wins for strings
    # that the grammar can otherwise segment in more than one way.
    _QUAL_RE: ClassVar[re.Pattern[str]] = re.compile(
        Cfg.cfg.data["qual-restrictor"]["re"],
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
        values = [Cfg.cfg.data["qual-restrictor"]["absent"]] * 5

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
        forms: set[str]
        triples: abc.Iterable[tuple[str, str, str]]
        forms = set()

        if field in Cfg.cfg.data["qual-restrictor"]["pre-aliases"]:
            triples = iterprod(
                Cfg.cfg.data["qual-restrictor"]["sep"],
                Cfg.cfg.data["qual-restrictor"]["pre-aliases"][field],
                Cfg.cfg.data["qual-restrictor"]["sep"],
            )
            for before, alias, after in triples:
                forms.add(before + alias + after)

        elif field == "post":
            # Implicit post-release spelling: ``-N``.  Unlike the explicit
            # spellings, it cannot use an implicit numeric value.
            if num:
                forms.add("-")
            for before in Cfg.cfg.data["qual-restrictor"]["sep"]:
                for alias in Cfg.cfg.data["qual-restrictor"]["post-aliases"]:
                    for after in Cfg.cfg.data["qual-restrictor"]["sep"]:
                        forms.add(before + alias + after)

        elif field == "dev":
            for before in Cfg.cfg.data["qual-restrictor"]["sep"]:
                for after in Cfg.cfg.data["qual-restrictor"]["sep"]:
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
            if num != Cfg.cfg.data["qual-restrictor"]["absent"]
        ]

        rows: set[QualRow] = set()
        base = [Cfg.cfg.data["qual-restrictor"]["absent"]] * 5

        cls._visit_literal_rows(text, present, 0, 0, base, rows)
        return rows

    @classmethod
    def _visit_literal_rows(
        cls,
        text: str,
        present: list[tuple[int, str, str]],
        which: int,
        pos: int,
        row: list[str],
        rows: set[QualRow],
    ) -> None:
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
            cls._visit_literal_rows(
                text, present, which + 1, end, next_row, rows
            )


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
class QualRestrictor:
    mag_row: tuple[int | None, int | None, int | None, int | None, int | None]
    lit_rows: frozenset[QualRow]

    _FORMAT_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"""
        \A
        (?P<a_f>[-_.]?(?:alpha|a)[-_.]?\#*)?
        (?P<b_f>[-_.]?(?:beta|b)[-_.]?\#*)?
        (?P<rc_f>[-_.]?(?:preview|pre|c|rc)[-_.]?\#*)?
        (?P<post_f>
            (?P<post_lit_f>
                (?P<post_hyphen_f>-)
                |
                (?P<post_head_f>[-_.]?(?:post|rev|r)[-_.]?)
            )
            (?P<post_num_f>\#*)
        )?
        (?P<dev_f>
            (?P<dev_head_f>[-_.]?dev[-_.]?)
            (?P<dev_num_f>\#*)
        )?
        \Z
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    _FIELDS: ClassVar[tuple[str, ...]] = QualRow._fields

    def best(self: Self, /) -> str:
        """Return the shortest qual format spec represented by this state.

        A literal row fixes the spelling of every qualifier segment that was
        actually observed.  Unobserved segments are free to use one of the
        minimal inactive spellings when that is needed to keep the format
        grammar from greedily assigning a separator to the wrong segment.

        Numeric magnitudes describe exactly which ``#`` widths preserve the
        observed digits.  Negative magnitudes permit harmless widths up to
        the shortest natural number, zero means that at least one example
        omitted the number entirely, and positive magnitudes require zero
        padding of that width.
        """
        candidates: set[str] = set()

        for row in self.lit_rows:
            groups = tuple(
                self._field_options(field, literal, mag)
                for field, literal, mag in zip(self._FIELDS, row, self.mag_row)
            )
            for parts in product(*groups):
                spec = "".join(parts)
                if self._matches(spec, row):
                    candidates.add(spec)

        if not candidates:
            raise ValueError
        return min(candidates, key=lambda spec: (len(spec), spec))

    @classmethod
    def _field_options(
        cls, field: str, literal: str, mag: int | None, /
    ) -> tuple[str, ...]:
        if mag is None:
            return tuple[str, ...](
                Cfg.cfg.data["qual-restrictor"]["inactive"][field]
            )

        options: list[str] = []
        if literal == Cfg.cfg.data["qual-restrictor"]["canon"][
            field
        ] and cls._always_num_ok(mag, 0):
            options.append("")

        limit = max(1, abs(mag))
        for width in range(limit + 1):
            if field == "post" and literal == "-":
                ok = cls._always_num_ok(mag, width)
            else:
                ok = cls._conditional_num_ok(mag, width)
            if ok:
                options.append(literal + "#" * width)

        return tuple(dict.fromkeys(options))

    @staticmethod
    def _conditional_num_ok(mag: int, width: int, /) -> bool:
        if mag > 0:
            return width == mag
        if mag == 0:
            return width == 0
        return 0 <= width <= -mag

    @staticmethod
    def _always_num_ok(mag: int, width: int, /) -> bool:
        if mag > 1:
            return width == mag
        if mag == 1:
            return width in (0, 1)
        if mag == 0:
            return False
        return 0 <= width <= -mag

    def _matches(self: Self, spec: str, row: QualRow, /) -> bool:
        cls = type(self)
        match = cls._FORMAT_RE.fullmatch(spec)
        if match is None:
            return False

        parsed: dict[str, tuple[bool, str, int]] = {}
        for field in ("a", "b", "rc"):
            token = match.group(field + "_f") or ""
            if token:
                head = token.rstrip("#")
                parsed[field] = (True, head, len(token) - len(head))
            else:
                parsed[field] = (False, "", 0)

        post_token = match.group("post_f") or ""
        if post_token:
            head = (
                match.group("post_hyphen_f")
                or match.group("post_head_f")
                or ""
            )
            parsed["post"] = (
                True,
                head,
                len(match.group("post_num_f") or ""),
            )
        else:
            parsed["post"] = (False, "", 0)

        dev_token = match.group("dev_f") or ""
        if dev_token:
            parsed["dev"] = (
                True,
                match.group("dev_head_f") or "",
                len(match.group("dev_num_f") or ""),
            )
        else:
            parsed["dev"] = (False, "", 0)

        for field, literal, mag in zip(cls._FIELDS, row, self.mag_row):
            if mag is None:
                continue
            present, head, width = parsed[field]
            if not present:
                if literal != Cfg.cfg.data["qual-restrictor"]["canon"][field]:
                    return False
                if not cls._always_num_ok(mag, 0):
                    return False
                continue
            if head != literal:
                return False
            if field == "post" and head == "-":
                if not cls._always_num_ok(mag, width):
                    return False
            elif not cls._conditional_num_ok(mag, width):
                return False

        return True

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        mag_row: list[int | None]
        qual_info: QualInfo
        qual_info = QualInfo.by_string(text)
        mag_row = list()
        for num in qual_info.num_row:
            if num == "?":
                mag_row.append(None)
            elif num.startswith("0"):
                mag_row.append(len(num))
            else:
                mag_row.append(-len(num))
        return cls(
            mag_row=tuple(mag_row),  # type: ignore[arg-type]
            lit_rows=qual_info.lit_rows,
        )

    def union(self: Self, other: Self, /) -> Self:
        mag_row = list()
        for a, b in zip(self.mag_row, other.mag_row):
            if a is None:
                mag_row.append(b)
            elif b is None:
                mag_row.append(a)
            elif a == b:
                mag_row.append(a)
            elif a + b <= 0:
                mag_row.append(max(a, b))
            else:
                raise ValueError
        lit_rows = set()
        for rowA in self.lit_rows:
            for rowB in other.lit_rows:
                lit_rows.update(lit_row_union(rowA, rowB))
        return type(self)(
            mag_row=tuple(mag_row),  # type: ignore[arg-type]
            lit_rows=frozenset(lit_rows),
        )
