from abc import abstractmethod
from typing import *

import setdoc
from copyable import Copyable
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440.errors.VersionError import VersionError

__all__ = ["CoreABC"]


class CoreABC(Copyable):
    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __eq__(self: Self, other: object) -> Any: ...

    @setdoc.basic
    def __format__(self: Self, format_spec: object) -> str:
        parsed: tuple[Any, ...]
        msg: str
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["format"]
            msg %= (format_spec, type(self).__name__)
            raise VersionError(msg)  # from None
        return str(self._format_parsed(parsed))

    @abstractmethod
    @setdoc.basic
    def __ge__(self: Self, other: Any) -> Any: ...

    @abstractmethod
    @setdoc.basic
    def __gt__(self: Self, other: Any) -> Any: ...

    @abstractmethod
    @setdoc.basic
    def __init__(self: Self, string: object) -> None: ...

    @abstractmethod
    @setdoc.basic
    def __le__(self: Self, other: Any) -> Any: ...

    @abstractmethod
    @setdoc.basic
    def __lt__(self: Self, other: Any) -> Any: ...

    @abstractmethod
    @setdoc.basic
    def __ne__(self: Self, other: object) -> Any: ...

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self) -> str: ...

    @setdoc.basic
    def __setattr__(self: Self, name: str, value: Any) -> None:
        a: Any
        backup: str
        msg: str
        target: str
        a = getattr(type(self), name, None)
        if (not isinstance(a, property)) or not hasattr(a, "fset"):
            object.__setattr__(self, name, value)
            return
        backup = str(self)
        try:
            object.__setattr__(self, name, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            msg = "%r is an invalid value for %r"
            target = type(self).__name__ + "." + name
            msg %= (value, target)
            raise VersionError(msg)

    @classmethod
    def __subclasshook__(cls: type[Self], other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @setdoc.basic
    def __str__(self: Self) -> str:
        return format(self, "")

    @classmethod
    @abstractmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]: ...

    @abstractmethod
    def _format_parsed(self: Self, parsed: tuple[Any, ...], /) -> object: ...

    @abstractmethod
    def _string_fset(self: Self, value: str) -> None: ...

    @setdoc.basic
    def copy(self: Self) -> Self:
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], *strings: Any) -> str:
        msg: str
        keys: tuple
        values: tuple
        info: dict[str, Self]
        keys = tuple(map(str, strings))
        values = tuple(map(cls, keys))
        info = dict(zip(keys, values))
        try:
            return cls._deformat(info)
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise TypeError(msg)

    @property
    @abstractmethod
    def packaging(self: Self) -> Any: ...

    @property
    def string(self: Self) -> str:
        "This property represents self as str."
        return format(self, "")

    @string.setter
    def string(self: Self, value: object) -> None:
        self._string_fset(str(value).lower())
