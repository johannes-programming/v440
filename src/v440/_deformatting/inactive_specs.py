"""Helpers for exact deformatting searches in v440 qualification classes."""

from __future__ import annotations

from v440._utils.Cfg import Cfg

__all__ = ["inactive_specs"]

# These are the shortest representatives of the syntactically useful forms of
# a token whose component is absent from every example.  Although such a token
# emits no text, it can be required as a fence between two neighbouring tokens
# in the combined regex grammar (for example ``B#`` in ``alphaB#.pre``).


def inactive_specs(pattern: str, /) -> tuple[str, ...]:
    return tuple(Cfg.cfg.data["inactive-specs"][pattern])
