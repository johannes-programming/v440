"""Helpers for exact deformatting searches in v440 qualification classes."""

from __future__ import annotations

__all__ = ["inactive_specs", "matching_specs", "token_specs"]

from collections.abc import Iterable, Sequence
from functools import lru_cache
from typing import Any, Literal

from v440._utils.Cfg import Cfg

Relation = Literal["contains", "exact", "prefix", "suffix"]

# The longest literal head in the qualification format grammar is
# ``.preview.`` (nine characters).  Hash marks, which describe numeric width,
# are added separately below.
_MAX_HEAD = 9

# These are the shortest representatives of the syntactically useful forms of
# a token whose component is absent from every example.  Although such a token
# emits no text, it can be required as a fence between two neighbouring tokens
# in the combined regex grammar (for example ``B#`` in ``alphaB#.pre``).
_INACTIVE: dict[str, tuple[str, ...]] = {
    "a_f": ("", "A", "A#"),
    "b_f": ("", "B", "B#"),
    "rc_f": ("", "C", "C#"),
    "post_f": ("", "-", "R", "-#", "R#"),
    "dev_f": ("", "DEV", "DEV#"),
}


def _matches(pattern: str, value: str, /) -> bool:
    try:
        Cfg.fullmatches(pattern, value)
    except Exception:
        return False
    return True


@lru_cache(maxsize=None)
def token_specs(pattern: str, body: str, /) -> tuple[str, ...]:
    """Return every token that can matter to a shortest spec for *body*.

    An explicit token head is emitted literally whenever its component is
    present.  Consequently, that head must occur in the example body.  A run
    of ``#`` characters cannot be longer than the body because a present
    component emits at least that many digits.
    """

    heads: set[str] = set()
    specs: set[str] = {""}
    n = len(body)
    for start in range(n):
        stop = min(n, start + _MAX_HEAD)
        for end in range(start + 1, stop + 1):
            head = body[start:end]
            if _matches(pattern, head):
                heads.add(head)
    for head in heads:
        for mag in range(n + 1):
            spec = head + "#" * mag
            if _matches(pattern, spec):
                specs.add(spec)
    return tuple(sorted(specs, key=lambda s: (len(s), s)))


def inactive_specs(pattern: str, /) -> tuple[str, ...]:
    return _INACTIVE[pattern]


def _related(output: str, body: str, relation: Relation, /) -> bool:
    if relation == "exact":
        return output == body
    if relation == "prefix":
        return body.startswith(output)
    if relation == "suffix":
        return body.endswith(output)
    if relation == "contains":
        return output in body
    raise ValueError(relation)


def matching_specs(
    objects: Sequence[Any],
    bodies: Sequence[str],
    specs: Iterable[str],
    relation: Relation,
    /,
) -> tuple[str, ...]:
    """Keep all specs whose emitted text has the requested body relation.

    Deliberately do not collapse specs with identical output.  A longer spec
    can act as a lexical fence when it is embedded in a larger format spec.
    """

    ans: set[str] = set()
    for spec in specs:
        try:
            outputs = tuple(format(obj, spec) for obj in objects)
        except Exception:
            continue
        if all(
            _related(output, body, relation)
            for output, body in zip(outputs, bodies)
        ):
            ans.add(spec)
    return tuple(sorted(ans, key=lambda s: (len(s), s)))
