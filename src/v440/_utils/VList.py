from datahold import OkayList
from v440._utils.Base import Base
from typing import *
import functools

class VList(Base, OkayList):

    @functools.wraps(OkayList.__add__)
    def __add__(self, other:Any, /) -> Self:
        other = type(self)(other)
        ans = self._data + other._data
        ans = type(self)(ans)
        return ans
    
    @functools.wraps(OkayList.__iadd__)
    def __iadd__(self, other:Any, /) -> Self:
        other = type(self)(other)
        self.data += other.data
    
    @functools.wraps(OkayList.__le__)
    def __le__(self, other:Any, /) -> bool:
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return self._data <= other._data
        return self.data <= other
    
    @functools.wraps(OkayList.__radd__)
    def __radd__(self, other:Any, /) -> Self:
        return type(self)(other) + self
    
    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans
    
    @functools.wraps(OkayList.extend)
    def extend(self, value:Any, /) -> None:
        self.__iadd__(value)
        

        