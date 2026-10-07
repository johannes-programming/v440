"""Restrict qualifier segments while deformatting versions."""

from __future__ import annotations

__all__: list[str] = ["QualRestrictor"]

from collections import abc
from dataclasses import dataclass
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

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        """Parse text as a PEP 440 qual, preserving literal splits."""
        lit_rows: set[QualRow]
        matches: dict[str, str]
        num_row: QualRow
        # num_row follows the configured PEP 440 qualifier pattern.
        # lit_rows holds every grammar-valid literal split of that numeric row.
        try:
            matches = Cfg.fullmatches("qual", text)
        except AttributeError as exc:
            raise ValueError(
                f"not a PEP 440-conforming qual: {text!r}"
            ) from exc

        num_row = cls._num_row_from_matches(matches)
        lit_rows = cls._all_literal_rows(text, num_row)

        # A successful reference parse must itself correspond to at least one
        # enumerated segmentation.  Keeping this as an internal assertion
        # catches accidental divergence between the two grammar definitions.
        assert lit_rows

        return cls(num_row=num_row, lit_rows=frozenset(lit_rows))

    @classmethod
    def _num_row_from_matches(
        cls: type[Self], matches: dict[str, str]
    ) -> QualRow:
        """Build the numeric row from configured qualifier matches."""
        index: int
        post_num: str
        pre_l: str
        values: list[str]
        values = [Cfg.cfg.data["qual-restrictor"]["absent"]] * 5

        pre_l = matches["pre_lit"]
        if pre_l:
            pre_l = pre_l.lower()
            if pre_l in {"alpha", "a"}:
                index = 0
            elif pre_l in {"beta", "b"}:
                index = 1
            else:
                index = 2
            values[index] = matches["pre_num"]

        if matches["post"]:
            post_num = matches["post_num"]
            if matches["post_hyphen_num"]:
                post_num = matches["post_hyphen_num"][1:]
            values[3] = post_num

        if matches["dev"]:
            values[4] = matches["dev_num"]

        return QualRow(*values)

    @classmethod
    def _literal_forms(
        cls: type[Self],
        /,
        field: str,
        num: str,
    ) -> tuple[str, ...]:
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
            triples = iterprod(
                Cfg.cfg.data["qual-restrictor"]["sep"],
                Cfg.cfg.data["qual-restrictor"]["post-aliases"],
                Cfg.cfg.data["qual-restrictor"]["sep"],
            )
            for before, alias, after in triples:
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
    def _all_literal_rows(
        cls: type[Self], text: str, num_row: QualRow
    ) -> set[QualRow]:
        """Handle all literal rows."""
        base: list[str]
        fields: tuple[str, ...]
        present: list[tuple[int, str, str]]
        rows: set[QualRow]
        fields = QualRow._fields
        present = [
            (index, field, num)
            for index, (field, num) in enumerate(zip(fields, num_row))
            if num != Cfg.cfg.data["qual-restrictor"]["absent"]
        ]
        rows = set()
        base = [Cfg.cfg.data["qual-restrictor"]["absent"]] * 5

        cls._visit_literal_rows(text, present, 0, 0, base, rows)
        return rows

    @classmethod
    def _visit_literal_rows(
        cls: type[Self],
        text: str,
        present: list[tuple[int, str, str]],
        which: int,
        pos: int,
        row: list[str],
        rows: set[QualRow],
    ) -> None:
        """Visit every literal segmentation of the remaining text."""
        digits: str
        end: int
        field: str
        index: int
        literal: str
        literal_pattern: str
        next_row: list[str]
        num: str
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
    """Unite two literal rows, or return no row."""
    a: str
    ans: list[str]
    b: str
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
    """Represent QualRestrictor."""

    mag_row: tuple[int | None, int | None, int | None, int | None, int | None]
    lit_rows: frozenset[QualRow]

    _FIELDS: ClassVar[tuple[str, ...]] = QualRow._fields

    def best(self: Self, /) -> str:
        """Return the shortest qual format spec represented by this state."""
        candidates: set[str]
        groups: map[tuple[str, ...]]
        row: QualRow
        # A literal row fixes observed spellings. Unobserved segments may use
        # a minimal inactive spelling so separators stay on the right segment.
        candidates = set()

        for row in self.lit_rows:
            groups = map(self._field_options, self._FIELDS, row, self.mag_row)
            specs = map("".join, iterprod(*groups))
            candidates.update(
                spec for spec in specs if self._matches(spec, row)
            )

        if not candidates:
            raise ValueError
        return min(candidates, key=lambda spec: (len(spec), spec))

    @classmethod
    def _field_options(
        cls: type[Self], field: str, literal: str, mag: int | None, /
    ) -> tuple[str, ...]:
        """Return format widths allowed for one qualifier field."""
        limit: int
        ok: bool
        options: list[str]
        width: int
        if mag is None:
            return tuple[str, ...](
                Cfg.cfg.data["qual-restrictor"]["inactive"][field]
            )

        options = []
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
        """Handle conditional num ok."""
        if mag > 0:
            return width == mag
        if mag == 0:
            return width == 0
        return 0 <= width <= -mag

    @staticmethod
    def _always_num_ok(mag: int, width: int, /) -> bool:
        """Handle always num ok."""
        if mag > 1:
            return width == mag
        if mag == 1:
            return width in (0, 1)
        if mag == 0:
            return False
        return 0 <= width <= -mag

    def _matches(self: Self, spec: str, row: QualRow, /) -> bool:
        """Report whether a spec still reproduces the observed row."""
        cls: type[QualRestrictor]
        dev_token: str
        field: str
        head: str
        literal: str
        mag: int | None
        matches: dict[str, str]
        parsed: dict[str, tuple[bool, str, int]]
        post_token: str
        present: bool
        token: str
        width: int
        cls = type(self)
        try:
            matches = Cfg.fullmatches("qual_f", spec)
        except AttributeError:
            return False

        parsed = {}
        for field in ("a", "b", "rc"):
            token = matches[field + "_f"]
            if token:
                head = token.rstrip("#")
                parsed[field] = (True, head, len(token) - len(head))
            else:
                parsed[field] = (False, "", 0)

        post_token = matches["post_f"]
        if post_token:
            head = matches["post_hyphen_f"] or matches["post_head"]
            parsed["post"] = (True, head, len(matches["post_num_f"]))
        else:
            parsed["post"] = (False, "", 0)

        dev_token = matches["dev_f"]
        if dev_token:
            parsed["dev"] = (
                True,
                matches["dev_head"],
                len(matches["dev_num_f"]),
            )
        else:
            parsed["dev"] = (False, "", 0)

        for field, literal, mag in zip(cls._FIELDS, row, self.mag_row):
            if mag is None:
                continue
            present, head, width = parsed[field]
            if not (
                present
                or literal == Cfg.cfg.data["qual-restrictor"]["canon"][field]
            ):
                return False
            if not (present or cls._always_num_ok(mag, 0)):
                return False
            if not present:
                continue
            if head != literal:
                return False
            if (
                field == "post"
                and head == "-"
                and not cls._always_num_ok(mag, width)
            ):
                return False
            if field == "post" and head == "-":
                continue
            if not cls._conditional_num_ok(mag, width):
                return False

        return True

    @classmethod
    def by_string(cls: type[Self], text: str, /) -> Self:
        """Build a restrictor from one qualifier string."""
        mag_row: list[int | None]
        num: str
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
        a: int | None
        b: int | None
        lit_rows: set[QualRow]
        mag_row: list[int | None]
        rowA: QualRow
        rowB: QualRow
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
