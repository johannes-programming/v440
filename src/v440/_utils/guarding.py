from __future__ import annotations

import functools
from typing import *

from v440.core.VersionError import VersionError


def guard(old: Any) -> Any:
    @functools.wraps(old)
    def new(self: Self, value: Any) -> None:
        backup: str = str(getattr(self, old.__name__))
        try:
            old(self, value)
        except VersionError:
            setattr(self, old.__name__, backup)
            raise
        except Exception:
            setattr(self, old.__name__, backup)
            msg: str = "%r is an invalid value for %r"
            target: str = type(self).__name__ + "." + old.__name__
            msg %= (value, target)
            raise VersionError(msg)

    return new
