"""Provide the CoreABC abstract base for v440 classes."""

__all__: list[str] = ["CoreABC"]

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Self

import setdoc
from copyable import Copyable
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.errors.VersionError import VersionError


def core_split(flat: str, /) -> tuple[str, str, str]:
    x: str
    y: str
    z: str
    y = flat.strip()
    if y:
        x, z = flat.split(y)
    elif flat:
        raise ValueError
    else:
        x, z = "", ""
    return x, y, z


class CoreABC(Copyable):
    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __eq__(self: Self, other: object, /) -> bool: ...

    @setdoc.basic
    def __format__(self: Self, format_spec: object, /) -> str:
        parsed: tuple[Any, ...]
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            raise ValueError(
                f"Invalid format specifier {format_spec} for object of type {type(self).__name__}!"
            ) from None
        return str(self._format_parsed(*parsed))

    @abstractmethod
    @setdoc.basic
    def __ge__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __gt__(self: Self, other: Self, /) -> bool: ...

    @setdoc.basic
    def __init__(
        self: Self, other: Self | None = None, /, **kwargs: Any
    ) -> None:
        self._init_other(other)
        self._init_kwargs(**kwargs)

    @abstractmethod
    @setdoc.basic
    def __le__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __lt__(self: Self, other: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self, /) -> str: ...

    @setdoc.basic
    def __str__(self: Self, /) -> str:
        return format(self, "")

    @abstractmethod
    def _deformat(self: Self, body: str) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]: ...

    @abstractmethod
    def _format_parsed(self: Self, /, *parsed: Any) -> object: ...

    def _init_kwargs(self: Self, /, **kwargs: Any) -> None:
        x: str
        y: Any
        for x, y in kwargs.items():
            setattr(self, x.lstrip("_"), y)

    @abstractmethod
    def _init_other(self: Self, other: Self | None, /) -> None: ...

    @abstractmethod
    def _string_fset(self: Self, value: str, /) -> None: ...

    @setdoc.basic
    def copy(self: Self, /) -> Self:
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        flat: str
        if strings == ():
            return ""
        flats = list(sorted(set(map(str, strings))))
        try:
            acc = cls(string=flats[0])._deformat(flats[0])
            for flat in flats[1:]:
                acc = acc.union(cls(string=flat)._deformat(flat))
            return acc.best()  # type: ignore[no-any-return]
        except VersionError:
            raise
        except Exception:
            msg = Cfg.cfg.data["errors"]["deformat"]
            msg %= oxford(*strings)
            raise VersionError(msg)

    @property
    @abstractmethod
    def packaging(self: Self, /) -> Any: ...

    @property
    def string(self: Self, /) -> str:
        "This property represents self as str."
        return format(self, "")

    @string.setter
    @setter
    def string(self: Self, value: object, /) -> None:
        self._string_fset(str(value).lower())
