from datahold import OkayList
from v440._utils.Base import Base
from typing import *

class VList(Base, OkayList):
    
    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans