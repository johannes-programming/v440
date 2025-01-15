from typing import *

__all__ = ["VersionError"]


class VersionError(ValueError):
    __slots__ = ("args",)

    def __init__(self, *args: Any):
        super().__init__(*args)
