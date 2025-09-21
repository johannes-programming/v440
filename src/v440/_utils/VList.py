from typing import *

from datahold import OkayList

from v440._utils.BaseList import BaseList
from v440.core.VersionError import VersionError


class VList(OkayList, BaseList):

    def __eq__(self: Self, other: Any) -> bool:
        "This magic method implements self==other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except VersionError:
            ans = False
        else:
            ans = self._data == alt._data
        return ans

    def __ge__(self: Self, other: Any, /) -> bool:
        "This magic method implements self>=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except Exception:
            ans = self.data >= other
        else:
            ans = alt <= self
        return ans

    def __iadd__(self: Self, other: Any, /) -> Self:
        "This magic method implements self+=other."
        self.data += type(self)(other).data
        return self

    def __imul__(self: Self, other: Any, /) -> Self:
        "This magic method implements self*=other."
        self.data = self.data * other
        return self

    def __le__(self: Self, other: Any, /) -> bool:
        "This magic method implements self<=other."
        ans: bool
        try:
            alt: Self = type(self)(other)
        except Exception:
            ans = self.data <= other
        else:
            ans = self._data <= alt._data
        return ans

    def __sorted__(self: Any, /, **kwargs: Any) -> Self:
        "This magic method implements sorted(self, **kwargs)."
        ans: Any = self.copy()
        ans.sort(**kwargs)
        return ans

    def isempty(self: Self) -> bool:
        return len(self) == 0
