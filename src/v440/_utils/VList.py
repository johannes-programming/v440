from typing import *

from datahold import OkayList

from v440._utils.Base import Base


class VList(Base, OkayList):
    def __iadd__(self, other, /):
        self._data += type(self)(other)._data
        return self

    def __imul__(self, other, /):
        self.data = self.data * other
        return self

    def __init__(self, data=None) -> None:
        self.data = data

    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans
