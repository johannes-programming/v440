"""Provide the VersionError exception for v440."""

__all__: list[str] = ["VersionError"]


class VersionError(ValueError):
    """Raise for invalid values passed to v440 properties."""

    pass
