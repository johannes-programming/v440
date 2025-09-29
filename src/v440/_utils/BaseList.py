import collections
from abc import abstractmethod
from typing import *

import scaevola
import setdoc
import unhash
from datarepr import datarepr

from v440._utils.utils import guard
from v440.core.VersionError import VersionError


@scaevola.auto
class BaseList(collections.abc.Collection):
    __slots__ = ()

    string: str

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    @setdoc.basic
    def __contains__(self: Self, other: Any) -> bool:
        return other in self.data

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> bool:
        try:
            alt: Self = type(self)(other)
        except VersionError:
            return False
        return self.data == alt.data

    @setdoc.basic
    def __format__(self: Self, format_spec: Any) -> str:
        try:
            return self._format(str(format_spec))
        except Exception:
            msg: str = "unsupported format string passed to %s.__format__"
            msg %= type(self).__name__
            raise TypeError(msg) from None

    @setdoc.basic
    def __ge__(self: Self, other: Any) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        return self._cmp() >= alt._cmp()

    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> Any:
        return self.data[key]

    @setdoc.basic
    def __gt__(self: Self, other: Any) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        return self._cmp() > alt._cmp()

    __hash__ = unhash

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self.data = data

    @setdoc.basic
    def __iter__(self: Self) -> Iterator:
        return iter(self.data)

    @setdoc.basic
    def __le__(self: Self, other: Any) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        return self._cmp() <= alt._cmp()

    @setdoc.basic
    def __lt__(self: Self, other: Any) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        return self._cmp() < alt._cmp()

    @setdoc.basic
    def __ne__(self: Self, other: Any) -> bool:
        return not (self == other)

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, self.data)

    @setdoc.basic
    def __reversed__(self: Self) -> reversed:
        return reversed(self.data)

    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> None:
        data: list = list(self.data)
        data[key] = value
        self.data = data

    @classmethod
    def __subclasshook__(cls: type, other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @setdoc.basic
    def __str__(self: Self) -> str:
        return self._format("")

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @abstractmethod
    def _format(self: Self, format_spec: str) -> str: ...

    @abstractmethod
    def _string_fset(self: Self, value: str) -> None: ...

    @setdoc.basic
    def copy(self: Self) -> Self:
        return type(self)(self)

    @property
    @abstractmethod
    @setdoc.basic
    def data(self: Self) -> tuple: ...

    def count(self: Self, value: Any) -> int:
        "This method counts the occurences of value."
        return self.data.count(value)

    def index(self: Self, *args: Any) -> None:
        "This method returns the index of the first occurence."
        return self.data.index(*args)

    @property
    def string(self: Self) -> str:
        return self._format("")

    @string.setter
    @guard
    def string(self: Self, value: Any) -> None:
        self._string_fset(str(value))
