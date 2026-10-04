"""Raise when a v440 mini-language operation fails."""

from __future__ import annotations

__all__: list[str] = ["MiniLangError"]
from v440.errors.VersionError import VersionError


class MiniLangError(VersionError):
    """Signal an invalid v440 formatting mini-language operation."""

    pass
