__all__: list[str] = ["setter"]

from collections import abc
from functools import wraps
from typing import Any, TypeVar, cast

from v440.errors.VersionError import VersionError

Function = TypeVar("Function", bound=abc.Callable[..., None])


def setter(function: Function, /) -> Function:
    """Restore an instance and normalize errors when its setter fails."""

    @wraps(function)
    def decorated(self: Any, value: object, /) -> None:
        backup: str
        msg: str
        target: str
        backup = str(self)
        try:
            function(self, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            msg = "%r is an invalid value for %r"
            target = type(self).__name__ + "." + function.__name__
            msg %= (value, target)
            raise VersionError(msg)

    return cast(Function, decorated)
