"""Provide the Release class for version release tuples in v440."""

from __future__ import annotations

__all__: list[str] = ["Release"]

import operator
import string as string_
from collections import abc
from typing import Any, Self, SupportsIndex, overload

import setdoc

from v440.abc.ListABC import ListABC


class Release(ListABC[int]):
    __slots__ = ()

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        i: int
        j: int
        k: int
        s: str
        t: str
        table: list[int]
        if len(info) == 0:
            return ""
        i = 0
        j = 0
        for s in info.keys():
            k = s.count(".")
            i = max(i, k + 1)
            t = s.rstrip("0")
            if t.endswith(".") or t == "":
                j = max(j, k)
        if j == 0:
            j = -1
        table = [0] * i
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(s.split(".")):
                k = cls._deformat_force(t)
                table[i] = cls._deformat_comb(table[i], k)
        s = ""
        for i, k in enumerate(table):
            if k > 1:
                s += "#" * k
            elif i == j:
                s += "#"
            s += "."
        s = s.rstrip(".")
        return s

    @classmethod
    def _deformat_force(cls: type[Self], part: str, /) -> int:
        if part == "0":
            return -1
        if part.startswith("0"):
            return len(part)
        return -len(part)

    @classmethod
    def _deformat_comb(cls: type[Self], x: int, y: int, /) -> int:
        if 0 > x * y:
            if x + y <= 0:
                return max(x, y)
            raise ValueError
        elif 0 < x * y:
            if x < 0:
                return max(x, y)
            if x == y:
                return x
            raise ValueError
        else:
            return x + y

    def _delitem(
        self: Self,
        /,
        *,
        key: Any,
        minlen: Any = None,
    ) -> None:
        packaging: list[int]
        packaging = self._list(minlen=minlen)
        del packaging[key]
        self.packaging = packaging

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[int, ...]:
        if spec.strip("#."):
            raise ValueError
        return tuple(map(len, spec.rstrip(".").split(".")))

    def _format_parsed(self: Self, /, *mags: int) -> str:
        packaging: list[int]
        parts: list[Any]
        packaging = list(self)
        packaging += [0] * max(0, len(mags) - len(self))
        parts = [f"0{m}d" for m in mags]
        parts += [""] * max(0, len(self) - len(mags))
        return ".".join(map(format, packaging, parts))

    @overload
    def _getitem(
        self: Self,
        /,
        *,
        key: SupportsIndex,
        minlen: SupportsIndex | None = None,
    ) -> int: ...
    @overload
    def _getitem(
        self: Self,
        /,
        *,
        key: slice,
        minlen: SupportsIndex | None = None,
    ) -> list[int]: ...
    def _getitem(
        self: Self,
        /,
        *,
        key: SupportsIndex | slice,
        minlen: SupportsIndex | None = None,
    ) -> int | list[int]:
        return self._list(minlen=minlen)[key]

    @classmethod
    def _item_parse(cls: type[Self], value: SupportsIndex, /) -> int:
        ans: int
        ans = operator.index(value)
        if ans < 0:
            raise ValueError
        return ans

    def _list(self: Self, /, minlen: SupportsIndex | None = None) -> list[int]:
        packaging: list[Any]
        index: Any
        packaging = list(self)
        if minlen is None:
            return packaging
        index = operator.index(minlen)
        packaging.extend([0] * max(0, index - len(self)))
        return packaging

    @classmethod
    def _mutable_parse(cls: type[Self], value: list[Any], /) -> list[int]:
        v: list[int]
        v = list(map(cls._item_parse, value))
        while v and v[-1] == 0:
            v.pop()
        return v

    def _setitem(
        self: Self,
        /,
        key: Any,
        value: Any,
        *,
        minlen: Any = None,
    ) -> None:
        packaging: list[int]
        packaging = self._list(minlen=minlen)
        packaging[key] = value
        self.packaging = packaging

    @classmethod
    def _sort(
        cls: type[Self],
        value: int,
        /,
    ) -> tuple[bool, int]:
        return True, value

    def _string_fset(
        self: Self,
        value: str,
        /,
    ) -> None:
        if value.strip(string_.digits + "."):
            raise ValueError
        self.packaging = map(int, value.split("."))

    def bump(
        self: Self,
        /,
        index: SupportsIndex = -1,
        amount: SupportsIndex = 1,
    ) -> None:
        a: int
        i: int
        mutable: list[int]
        a = operator.index(amount)
        i = operator.index(index)
        with self.__mutate__() as mutable:
            if i < len(self):
                mutable[i] += a
            else:
                mutable.extend([0] * (i - len(self)))
                mutable.append(a)

    @property
    def major(self: Self, /) -> int:
        "This property represents the version major."
        return self._getitem(key=0, minlen=1)

    @major.setter
    def major(self: Self, value: Any, /) -> None:
        self._setitem(key=0, value=value, minlen=1)

    @major.deleter
    def major(self: Self, /) -> None:
        self._delitem(key=0, minlen=1)

    @property
    def minor(self: Self, /) -> int:
        "This property represents the version minor."
        return self._getitem(key=1, minlen=2)

    @minor.setter
    def minor(self: Self, value: Any, /) -> None:
        self._setitem(key=1, value=value, minlen=2)

    @minor.deleter
    def minor(self: Self, /) -> None:
        self._delitem(key=1, minlen=2)

    @property
    def micro(self: Self, /) -> int:
        "This property represents the version micro."
        return self._getitem(key=2, minlen=3)

    @micro.setter
    def micro(self: Self, value: Any, /) -> None:
        self._setitem(key=2, value=value, minlen=3)

    @micro.deleter
    def micro(self: Self, /) -> None:
        self._delitem(key=2, minlen=3)

    patch = micro

    @property
    @setdoc.basic
    def packaging(self: Self, /) -> tuple[int, ...]:
        return self.__freeze__()

    @packaging.setter
    def packaging(self: Self, other: abc.Iterable[int], /) -> None:
        mutable: list[int]
        with self.__mutate__() as mutable:
            mutable.clear()
            mutable.extend(other)

    @setdoc.basic
    def sort(
        self: Self,
        /,
        *,
        key: Any = None,
        reverse: Any = False,
    ) -> None:
        with self.__mutate__() as mutable:
            mutable.sort(key=key, reverse=reverse)
