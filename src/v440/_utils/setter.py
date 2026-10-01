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
        backup: str
        msg: str
        backup = str(self)
        try:
            function(self, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            msg = Cfg.cfg.data["errors"]["setter"]
            msg = msg.format(
                Self=type(self).__name__,
                Value=type(value).__name__,
                func=function.__name__,
                value=value,
            )
            raise PEP440Error(msg) from None

    return cast(Function, decorated)
