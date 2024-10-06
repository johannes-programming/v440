from datahold import OkayList
from v440._utils.Base import Base
from typing import *
import functools

class VList(Base, OkayList):
    @functools.wraps(OkayList.__add__)
    def __add__(self, value:Any, /) ->Self:
        value = type(self)(value)
        ans = self.copy()
        ans.extend(value)
        return ans
    
    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans
    
    @functools.wraps(OkayList.__iadd__)
    def __iadd__(self, value:Any, /) ->None:
        value = type(self)(value)
        self.data += value.data


    @functools.wraps(OkayList.extend)
    def extend(self, value:Any, /) ->None:
        self += value