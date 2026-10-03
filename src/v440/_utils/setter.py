"""Wrap property setters so failures restore the instance."""

from __future__ import annotations

__all__: list[str] = ["setter"]

from collections import abc
from functools import wraps
from typing import Any, TypeVar, cast

from v440._utils.Cfg import Cfg
from v440.errors.PEP440Error import PEP440Error
from v440.errors.VersionError import VersionError

Function = TypeVar("Function", bound=abc.Callable[..., None])


def setter(function: Function, /) -> Function:
    """Restore an instance and normalize errors when its setter fails."""

    @wraps(function)
    def decorated(self: Any, value: object, /) -> None:
        """Apply the setter transactionally, restoring the previous value on failure."""
        backup: str
        message: str
        # Setters are transactional: retain the canonical rendering so a failed
        # mutation can restore the object before the normalized error is raised.
        backup = str(self)
        try:
            function(self, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            message = Cfg.cfg.data["errors"]["setter"]
            message = message.format(
                Self=type(self).__name__,
                Value=type(value).__name__,
                func=function.__name__,
                value=value,
            )
            raise PEP440Error(message) from None

    return cast(Function, decorated)
