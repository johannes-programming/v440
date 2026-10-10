"""Provide the Release class for version release tuples in v440."""

from __future__ import annotations

__all__: list[str] = ["Release"]

import operator
import string as string_
from typing import Any, Self, SupportsIndex, overload

from v440._deformatting.ReleaseRestrictor import ReleaseRestrictor
from v440._utils.setter import setter
from v440.abc.ListABC import ListABC


class Release(ListABC[int]):
    """Store normalized numeric release components."""

    __slots__ = ()

    @classmethod
    def _data_parse(cls: type[Self], /, *value: SupportsIndex) -> list[int]:
        """Normalize release items and remove insignificant trailing zeros."""
        parsed: list[int]
        parsed = list(map(item_parse, value))
        while parsed and parsed[-1] == 0:
            parsed.pop()
        return parsed

    def _deformat(self: Self, string: str, /) -> ReleaseRestrictor:
        """Infer formatting constraints from one release-component rendering."""
        return ReleaseRestrictor.by_string(string)

    def _delitem(
        self: Self,
        /,
        key: Any,
        *,
        minlen: Any = None,
    ) -> None:
        """Delete release components while honoring an optional minimum length."""
        data: list[int]
        data = self._list(minlen=minlen)
        del data[key]
        self.data = data

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> tuple[Any, ...]:
        """Parse a release format specification into numeric field widths."""
        if spec.strip("#."):
            raise ValueError
        return tuple(map(len, spec.rstrip(".").split(".")))

    def _format_parsed(self: Self, /, *mags: Any) -> str:
        """Render release components with the requested numeric field widths."""
        data: list[int]
        parts: list[Any]
        data = list(self)
        data += [0] * max(0, len(mags) - len(self))
        parts = [f"0{magnitude}d" for magnitude in mags]
        parts += [""] * max(0, len(self) - len(mags))
        return ".".join(map(format, data, parts))

    @overload
    def _getitem(
        self: Self,
        /,
        key: SupportsIndex,
        *,
        minlen: SupportsIndex | None = None,
    ) -> int: ...
    @overload
    def _getitem(
        self: Self,
        /,
        key: slice,
        *,
        minlen: SupportsIndex | None = None,
    ) -> list[int]: ...

    def _getitem(
        self: Self,
        /,
        key: SupportsIndex | slice,
        *,
        minlen: SupportsIndex | None = None,
    ) -> int | list[int]:
        """Return sequence items while honoring the requested minimum length."""
        return self._list(minlen=minlen)[key]

    def _list(self: Self, /, minlen: SupportsIndex | None = None) -> list[int]:
        """Return release components padded to the requested minimum length."""
        data: list[Any]
        index: Any
        data = list(self)
        if minlen is None:
            return data
        index = operator.index(minlen)
        data.extend([0] * max(0, index - len(self)))
        return data

    def _setitem(
        self: Self, /, key: Any, value: Any, *, minlen: Any = None
    ) -> None:
        """Assign sequence items while honoring the requested minimum length."""
        data: list[int]
        data = self._list(minlen=minlen)
        data[key] = value
        self.data = data

    @classmethod
    def _sort(cls: type[Self], value: int, /) -> tuple[bool, int]:
        """Return the comparison key for one normalized sequence item."""
        return True, value

    def _string_fset(self: Self, value: str, /) -> None:
        """Parse a string into this instance's normalized fields."""
        if value.strip(string_.digits + "."):
            raise ValueError
        self.data = map(int, value.split("."))

    def bump(
        self: Self, /, index: SupportsIndex = -1, amount: SupportsIndex = 1
    ) -> None:
        """Increment one release component and discard less-significant components."""
        data: list[int]
        increment: int
        target_index: int
        increment = operator.index(amount)
        target_index = operator.index(index)
        data = list(self)
        if target_index == -1:
            data[-1] += increment
        elif target_index < len(self):
            data[target_index] += increment
            data = data[: target_index + 1]
        else:
            data.extend((0,) * (target_index - len(self)))
            data.append(increment)
        self.data = data

    @property
    def major(self: Self, /) -> int:
        """Return the major release component."""
        return self._getitem(key=0, minlen=1)

    @major.setter
    @setter
    def major(self: Self, value: Any, /) -> None:
        """Set the major release component."""
        self._setitem(key=0, value=value, minlen=1)

    @major.deleter
    def major(self: Self, /) -> None:
        """Delete the major release component."""
        self._delitem(key=0, minlen=1)

    @property
    def minor(self: Self, /) -> int:
        """Return the minor release component."""
        return self._getitem(key=1, minlen=2)

    @minor.setter
    @setter
    def minor(self: Self, value: Any, /) -> None:
        """Set the minor release component."""
        self._setitem(key=1, value=value, minlen=2)

    @minor.deleter
    def minor(self: Self, /) -> None:
        """Delete the minor release component."""
        self._delitem(key=1, minlen=2)

    @property
    def micro(self: Self, /) -> int:
        """Return the micro release component."""
        return self._getitem(key=2, minlen=3)

    @micro.setter
    @setter
    def micro(self: Self, value: Any, /) -> None:
        """Set the micro release component."""
        self._setitem(key=2, value=value, minlen=3)

    @micro.deleter
    def micro(self: Self, /) -> None:
        """Delete the micro release component."""
        self._delitem(key=2, minlen=3)

    packaging = ListABC.data
    patch = micro

    def sort(self: Self, /, *, key: Any = None, reverse: Any = False) -> None:
        """Sort the release components in place."""
        self.data = sorted(self, key=key, reverse=reverse)


def item_parse(value: SupportsIndex, /) -> int:
    """Convert one release component to a nonnegative integer."""
    ans: int
    ans = operator.index(value)
    if ans < 0:
        raise ValueError
    return ans
