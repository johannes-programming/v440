from datahold import OkayList
from overloadable import overloadable
from v440._utils.Base import Base
from typing import *
import functools
import abc

class VList(Base, OkayList, abc):
    @functools.wraps(OkayList.__add__)
    def __add__(self, value:Any, /) ->Self:
        ans = self.copy()
        ans += value
        return ans
    
    @overloadable
    def __setitem__(self, key, value):
        return type(key) is slice
    @__setitem__.overload(False)
    def __setitem__(self, key, value):
        data = self.data
        data[key] = value
        self.data = data
    @__setitem__.overload(True)
    def __setitem__(self, key, value):

        value = self._tolist(value)
    
    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans
    
    @functools.wraps(OkayList.__iadd__)
    def __iadd__(self, value:Any, /) ->None:
        value = self._tolist(value)
        value = self.data + value
        self.data = value
    
    @classmethod
    @abc.abstractmethod
    def _tolist(cls, value, length="none"):...
        
        

    @functools.wraps(OkayList.extend)
    def extend(self, value:Any, /) ->None:
        self += value