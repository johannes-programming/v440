"""Provide the CoreABC abstract base for v440 classes."""

from __future__ import annotations

__all__: list[str] = ["CoreABC"]

from abc import abstractmethod
from typing import Any, Self

import setdoc
from copyable import Copyable
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440._utils.setter import setter
from v440.errors.MiniLangError import MiniLangError
from v440.errors.VersionError import VersionError


class CoreABC(Copyable):
    """Define shared construction, formatting, copying, and string behavior for version components."""

    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __eq__(self: Self, other: object, /) -> bool: ...

    @setdoc.basic
    def __format__(self: Self, format_spec: object, /) -> str:
        """Render this object according to a v440 format specification."""
        msg: str
        parsed: tuple[Any, ...]
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            msg = Cfg.cfg.data["errors"]["format"]
            msg = msg.format(
                Self=type(self).__name__,
                spec=format_spec,
            )
            raise MiniLangError(msg) from None
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
        """Initialize this object from another instance, a string value, and keyword overrides."""
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
        """Return the canonical string representation of this object."""
        return format(self, "")

    @abstractmethod
    def _deformat(self: Self, string: str, /) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]: ...

    @abstractmethod
    def _format_parsed(self: Self, /, *parsed: Any) -> object: ...

    def _init_kwargs(self: Self, /, **kwargs: Any) -> None:
        """Apply constructor keyword overrides to public component attributes."""
        name: str
        value: Any
        for name, value in kwargs.items():
            setattr(self, name.lstrip("_"), value)

    @abstractmethod
    def _init_other(self: Self, other: Self | None, /) -> None: ...

    @abstractmethod
    def _string_fset(self: Self, value: str, /) -> None: ...

    @setdoc.basic
    def copy(self: Self, /) -> Self:
        """Return an independent copy of this object."""
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        """Infer one format specification that reproduces all supplied renderings."""
        acc: Any
        flat: str
        flats: list[str]
        msg: str
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
            msg = msg.format(oxford=oxford(*map(repr, flats)))
            raise MiniLangError(msg)

    @property
    @abstractmethod
    def packaging(self: Self, /) -> Any: ...

    @property
    def string(self: Self, /) -> str:
        """Return the canonical string representation of this object."""
        return format(self, "")

    @string.setter
    @setter
    def string(self: Self, value: object, /) -> None:
        """Replace this object's state from the supplied string-compatible value."""
        text: str
        text = str(value)
        if not text.strip().isascii():
            raise ValueError
        self._string_fset(text.lower())


def core_split(flat: str, /) -> tuple[str, str, str]:
    """Split surrounding whitespace from a core version string."""
    core: str
    leading: str
    trailing: str
    core = flat.strip()
    if core:
        leading, trailing = flat.split(core)
    elif flat:
        raise ValueError
    else:
        leading, trailing = "", ""
    return leading, core, trailing
