import collections
from abc import abstractmethod
from typing import *

import scaevola
import setdoc
from datarepr import datarepr
from unhash import unhash

from v440._utils.BaseList import BaseList
from v440.core.VersionError import VersionError

__all__ = ["SlotList"]


@scaevola.auto
class SlotList(collections.abc.Collection, BaseList):
    __slots__ = ()

    data: list

    @setdoc.basic
    def __contains__(self: Self, other: Any) -> bool:
        return other in self.data

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> bool:
        try:
            alt: Self = type(self)(other)
        except VersionError:
            return False
        else:
            return self.data == alt.data

    @setdoc.basic
    def __format__(self: Self, format_spec: Any = "", /) -> str:
        return format(str(self), str(format_spec))

    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> Any:
        return self.data[key]

    @setdoc.basic
    def __ge__(self: Self, other: Any, /) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        else:
            return self._cmp() >= alt._cmp()

    @setdoc.basic
    def __gt__(self: Self, other: Any, /) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        else:
            return self._cmp() > alt._cmp()

    __hash__ = unhash

    @setdoc.basic
    def __init__(self: Self, data: Any = None) -> None:
        self.data = data

    @setdoc.basic
    def __iter__(self: Self) -> Any:
        return iter(self.data)

    @setdoc.basic
    def __le__(self: Self, other: Any, /) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        else:
            return self._cmp() <= alt._cmp()

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(type(self).__slots__)

    @setdoc.basic
    def __lt__(self: Self, other: Any, /) -> bool:
        alt: Self
        try:
            alt = type(self)(other)
        except VersionError:
            return NotImplemented
        else:
            return self._cmp() < alt._cmp()

    @setdoc.basic
    def __ne__(self: Self, other: Any) -> bool:
        return not (self == other)

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, self.data)

    @setdoc.basic
    def __reversed__(self: Self) -> Iterable:
        return reversed(self.data)

    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> None:
        data: list = self.data
        data[key] = value
        self.data = data

    @setdoc.basic
    def __str__(self: Self) -> str:
        return NotImplemented

    @classmethod
    def __subclasshook__(cls: type, other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    def _cmp(self: Self) -> Any:
        return self.data

    def copy(self: Self) -> Self:
        return type(self)(self)

    def count(self: Self, value: Any) -> Any:
        return self.data.count(value)

    @property
    @abstractmethod
    def data(self: Self) -> list: ...

    def index(self: Self, value: Any) -> Any:
        return self.data.index(value)
