import datahold
from scaevola import Scaevola
from v440._utils import utils

class VList(datahold.OkayList, Scaevola):
    
    def __sorted__(self, /, **kwargs) -> Self:
        ans = self.copy()
        ans.sort(**kwargs)
        return ans
    
    @functools.wraps(datahold.OkayList.count)
    def count(self, value:Any, /) -> int:
        value = utils.segment(value)
        return self._data.count(value)