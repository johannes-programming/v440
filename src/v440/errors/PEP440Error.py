__all__: list[str] = ["PEP440Error"]
from .VersionError import VersionError


class PEP440Error(VersionError):
    """Raise for invalid values passed to v440 properties."""

    pass
