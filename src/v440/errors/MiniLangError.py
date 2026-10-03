"""Raise when a v440 mini-language operation fails."""
__all__: list[str] = ["MiniLangError"]
from .VersionError import VersionError


class MiniLangError(VersionError):
    """Represent MiniLangError."""
    pass
