from typing import *

from datahold import OkayList

from v440.core.VersionError import VersionError

import abc



def clone(value: Any) -> Any:
    if isinstance(value, VList):
        return list(map(clone, value))
    else:
        return value


class VList(OkayList):
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
        except:
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
        except:
            ans = self.data <= other
        else:
            ans = self._data <= alt._data
        return ans

    def __setattr__(self: Self, name: str, value: Any) -> None:
        if name in type(self).__annotations__.keys():
            object.__setattr__(self, name, value)
            return
        backup: list = clone(self)
        exc: Exception
        try:
            object.__setattr__(self, name, value)
        except Exception as exc:
            self.data = backup
            if isinstance(exc, VersionError):
                raise
            msg: str = "%r is an invalid value for %r"
            msg %= (value, type(self).__name__ + "." + name)
            raise VersionError(msg)

    def __sorted__(self: Any, /, **kwargs: Any) -> Self:
        "This magic method implements sorted(self, **kwargs)."
        ans: Any = self.copy()
        ans.sort(**kwargs)
        return ans
    
    @abc.abstractmethod
    def isempty(self:Self)->bool:
        ...
    
