"""Provide transactional property setters for v440."""

__all__: list[str] = ["setter"]

from collections.abc import Callable
from functools import wraps
from typing import Protocol, cast

from v440._utils.Cfg import Cfg
from v440.errors.VersionError import VersionError


class _Settable(Protocol):
    @property
    def string(self, /) -> str: ...

    @string.setter
    def string(self, other: object, /) -> None: ...

    def _string_fset(self, other: str, /) -> None: ...


def setter[Function: Callable[..., None]](
    function: Function,
    /,
) -> Function:
    """Restore an instance and normalize errors when its setter fails."""

    @wraps(function)
    def decorated(self: object, value: object, /) -> None:
        backup: str
        settable: _Settable
        settable = cast(_Settable, self)
        backup = str(settable)
        try:
            function(self, value)
        except (TypeError, VersionError):
            settable.string = backup
            raise
        except Exception:
            settable._string_fset(backup.lower())
            raise Cfg.error(
                "setattr",
                VersionError,
                name=type(self).__name__ + "." + function.__name__,
                value=value,
            ) from None

    return cast(Function, decorated)
