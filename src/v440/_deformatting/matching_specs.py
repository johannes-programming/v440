"""Helpers for exact deformatting searches in v440 qualification classes."""

from __future__ import annotations

__all__ = ["matching_specs"]

from collections.abc import Iterable, Sequence
from typing import Any, Literal

Relation = Literal["contains", "exact", "prefix", "suffix"]


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
