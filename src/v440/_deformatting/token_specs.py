"""Helpers for exact deformatting searches in v440 qualification classes."""

from __future__ import annotations

__all__ = ["token_specs"]

from functools import lru_cache
from typing import Literal

from v440._utils.Cfg import Cfg

Relation = Literal["contains", "exact", "prefix", "suffix"]

# The longest literal head in the qualification format grammar is
# ``.preview.`` (nine characters).  Hash marks, which describe numeric width,
# are added separately below.
_MAX_HEAD = 9


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
