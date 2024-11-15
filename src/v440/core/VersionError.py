from typing import *

__all__ = ["VersionError"]


class VersionError(ValueError):
    def __init__(self, *args: Any):
        super().__init__(*args)
