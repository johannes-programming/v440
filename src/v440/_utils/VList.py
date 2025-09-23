from typing import *

import setdoc
from datahold import OkayList

from v440._utils.BaseList import BaseList
from v440.core.VersionError import VersionError


class VList(OkayList, BaseList):

    __slots__ = ()

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> bool:
        ans: bool
        try:
            alt: Self = type(self)(other)
        except VersionError:
            ans = False
        else:
            ans = self._data == alt._data
        return ans

    @setdoc.basic
    def __ge__(self: Self, other: Any, /) -> bool:
        ans: bool
        try:
            alt: Self = type(self)(other)
        except Exception:
            ans = self.data >= other
        else:
            ans = alt <= self
        return ans

    @setdoc.basic
    def __iadd__(self: Self, other: Any, /) -> Self:
        self.data += type(self)(other).data
        return self

    @setdoc.basic
    def __imul__(self: Self, other: Any, /) -> Self:
        self.data = self.data * other
        return self

    @setdoc.basic
    def __le__(self: Self, other: Any, /) -> bool:
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
