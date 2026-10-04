"""Raise when a v440 property receives an invalid value."""

from __future__ import annotations

__all__: list[str] = ["PEP440Error"]
from v440.errors.VersionError import VersionError


class PEP440Error(VersionError):
    """Raise for invalid values passed to v440 properties."""

    pass
