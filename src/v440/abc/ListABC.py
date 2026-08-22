"""Provide the ListABC abstract base for list-like v440 classes."""

from __future__ import annotations

__all__: list[str] = ["ListABC"]

import contextlib
from abc import abstractmethod
from collections import abc
from functools import cmp_to_key
from typing import Any, Protocol, Self, overload

import setdoc
from datahold import ListLike, MutableListSlot

from v440.abc.CoreABC import CoreABC


class SupportsDunderGE[Other, Return](Protocol):
    def __ge__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderGT[Other, Return](Protocol):
    def __gt__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderLE[Other, Return](Protocol):
    def __le__(self: Any, other: Other, /) -> Return: ...
class SupportsDunderLT[Other, Return](Protocol):
    def __lt__(self: Any, other: Other, /) -> Return: ...


class ListABC[Item: int | str](  # type: ignore[misc]
    MutableListSlot[Item],
    CoreABC,
):

    __slots__ = ()

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    @overload  # type: ignore[override]
    def __ge__[Item_, Return](
        self: ListLike[SupportsDunderGE[Item_, Return]],
        other: ListLike[Item_],
        /,
    ) -> Return: ...
    @overload
    def __ge__[Return](
        self: ListLike[Item],
        other: ListLike[SupportsDunderLE[Item, Return]],
        /,
    ) -> Return: ...
    @overload
    def __ge__(
        self: ListABC[Any],
        other: ListABC[Any],
        /,
    ) -> bool: ...
    def __ge__(self: Any, other: ListLike[Any], /) -> Any:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) >= tuple(map(cmpkey, other))
        else:
            return ListLike.__ge__(self, other)

    @overload  # type: ignore[override]
    def __gt__[Item_, Return](
        self: ListLike[SupportsDunderGT[Item_, Return]],
        other: ListLike[Item_],
        /,
    ) -> Return: ...
    @overload
    def __gt__[Return](
        self: ListLike[Item],
        other: ListLike[SupportsDunderLT[Item, Return]],
        /,
    ) -> Return: ...
    @overload
    def __gt__(
        self: ListABC[Any],
        other: ListABC[Any],
        /,
    ) -> bool: ...
    def __gt__(self: Any, other: ListLike[Any], /) -> Any:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) > tuple(map(cmpkey, other))
        else:
            return ListLike.__gt__(self, other)

    @setdoc.basic
    def __init__(
        self: Self,
        other: abc.Iterable[Item] | None = None,
        /,
        **kwargs: Any,
    ) -> None:
        self._init_other(other)
        self._init_kwargs(**kwargs)

    @overload  # type: ignore[override]
    def __le__[Item_, Return](
        self: ListLike[SupportsDunderLE[Item_, Return]],
        other: ListLike[Item_],
        /,
    ) -> Return: ...
    @overload
    def __le__[Return](
        self: ListLike[Item],
        other: ListLike[SupportsDunderGE[Item, Return]],
        /,
    ) -> Return: ...
    @overload
    def __le__(
        self: ListABC[Any],
        other: ListABC[Any],
        /,
    ) -> bool: ...
    def __le__(self: Any, other: ListLike[Any], /) -> Any:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) <= tuple(map(cmpkey, other))
        else:
            return ListLike.__le__(self, other)

    @overload  # type: ignore[override]
    def __lt__[Item_, Return](
        self: ListLike[SupportsDunderLT[Item_, Return]],
        other: ListLike[Item_],
        /,
    ) -> Return: ...
    @overload
    def __lt__[Return](
        self: ListLike[Item],
        other: ListLike[SupportsDunderGT[Item, Return]],
        /,
    ) -> Return: ...
    @overload
    def __lt__(
        self: ListABC[Any],
        other: ListABC[Any],
        /,
    ) -> bool: ...
    def __lt__(self: Any, other: ListLike[Any], /) -> Any:
        if isinstance(other, ListABC):
            return tuple(map(cmpkey, self)) < tuple(map(cmpkey, other))
        else:
            return ListLike.__lt__(self, other)

    @contextlib.contextmanager
    @setdoc.basic
    def __mutate__(self: Self, /) -> abc.Generator[list[Item], None, None]:
        mutable: list[Item]
        mutable = list(getattr(self, "_slot", ()))
        yield mutable
        self._slot = tuple(self._data_parse(mutable))

    @classmethod
    @setdoc.basic
    def __type__(
        cls,
        other: abc.Iterable[Item],
        /,
    ) -> Self:
        return cls(
            other,
        )

    @classmethod
    @abstractmethod
    def _data_parse(
        cls: type[Self], value: list[Any]
    ) -> abc.Iterable[Item]: ...

    def _init_other(self: Self, other: abc.Iterable[Item] | None, /) -> None:
        if other is None:
            MutableListSlot.__init__(self)
        else:
            MutableListSlot.__init__(self, other)

    @property
    @setdoc.basic
    def data(self: Self, /) -> tuple[Item, ...]:
        return self.__frozen__()

    @data.setter
    def data(self: Self, other: abc.Iterable[Item], /) -> None:
        mutable: list[Item]
        with self.__mutate__() as mutable:
            mutable.clear()
            mutable.extend(other)

    @setdoc.basic
    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        self.data = sorted(
            self,
            key=cmp_to_key(cmp) if key is None else key,
            reverse=reverse,
        )


def cmp(x: Any, y: Any) -> Any:
    """Compare two values with PEP 440 style for mixed int/str."""
    i: int
    if x is y or x == y:
        return 0
    try:
        if x <= y:
            return -1
        else:
            return 1
    except Exception:
        i = bool(isinstance(x, int)) - bool(isinstance(y, int))
        if i == 0:
            raise
        else:
            return i


def cmpkey(x: int | str, /) -> tuple[bool, int | str]:
    """Return key for sorting int before str."""
    return isinstance(x, int), x
