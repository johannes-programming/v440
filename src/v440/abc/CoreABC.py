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
from v440.errors.PEP440Error import PEP440Error
from v440.errors.VersionError import VersionError


class CoreABC(Copyable):
    """Define the shared parsing, formatting, copying, and error-handling interface."""

    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self, /) -> bool: ...

    @abstractmethod
    @setdoc.basic
    def __eq__(self: Self, other: object, /) -> bool: ...

    @setdoc.basic
    def __format__(self: Self, format_spec: object, /) -> str:
        """Render this value with the v440 format mini-language."""
        message: str
        parsed: tuple[Any, ...]
        # The format mini-language is user-facing, so implementation errors are
        # normalized to MiniLangError rather than leaking parser internals.
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            message = Cfg.cfg.data["errors"]["format"]
            message = message.format(
                Self=type(self).__name__,
                spec=format_spec,
            )
            raise MiniLangError(message) from None
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
        """Initialize this value from an optional source and keyword overrides."""
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
        """Render this value with its default format specification."""
        return format(self, "")

    @abstractmethod
    def _deformat(self: Self, body: str) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]: ...

    @abstractmethod
    def _format_parsed(self: Self, /, *parsed: Any) -> object: ...

    def _init_kwargs(self: Self, /, **kwargs: Any) -> None:
        """Apply keyword overrides to the corresponding public attributes."""
        attribute_name: str
        attribute_value: Any
        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name.lstrip("_"), attribute_value)

    @abstractmethod
    def _init_other(self: Self, other: Self | None, /) -> None: ...

    @abstractmethod
    def _string_fset(self: Self, value: str, /) -> None: ...

    @setdoc.basic
    def copy(self: Self, /) -> Self:
        """Return an independent copy of this value."""
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        """Infer a shortest format specification reproducing the supplied strings."""
        message: str
        rendering: str
        renderings: list[str]
        restriction: Any
        if strings == ():
            return ""
        # Sorting and deduplicating makes the inferred specification independent
        # of input order while avoiding redundant unions of identical renderings.
        renderings = list(sorted(set(map(str, strings))))
        try:
            restriction = cls(string=renderings[0])._deformat(renderings[0])
            for rendering in renderings[1:]:
                restriction = restriction.union(
                    cls(string=rendering)._deformat(rendering)
                )
            return restriction.best()  # type: ignore[no-any-return]
        except VersionError:
            raise
        except Exception:
            message = Cfg.cfg.data["errors"]["deformat"]
            message = message.format(oxford=oxford(*map(repr, renderings)))
            raise MiniLangError(message)

    @property
    @abstractmethod
    def packaging(self: Self, /) -> Any: ...

    @property
    def string(self: Self, /) -> str:
        """Return this value in canonical string form."""
        return format(self, "")

    @string.setter
    @setter
    def string(self: Self, value: object, /) -> None:
        """Parse and assign this value from a string-compatible object."""
        self._string_fset(str(value).lower())


def core_split(flat: str, /) -> tuple[str, str, str]:
    """Split a flat value into leading whitespace, body, and trailing whitespace."""
    leading: str
    body: str
    trailing: str
    body = flat.strip()
    if body:
        leading, trailing = flat.split(body)
    elif flat:
        raise ValueError
    else:
        leading, trailing = "", ""
    return leading, body, trailing
