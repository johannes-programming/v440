from v440.core.VersionError import VersionError
from typing import *
from datahold import OkayABC, OkayList
import functools

class Base(OkayABC):
    
    def __eq__(self, other: Any) -> bool:
        try:
            other = type(self)(other)
        except VersionError:
            return False
        return self._data == other._data
    
    @functools.wraps(OkayABC.__ge__)
    def __ge__(self, other:Any, /) -> bool:
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return other <= self
        return self.data >= other
    
    __gt__ = OkayList.__gt__
    __lt__ = OkayList.__lt__

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        cls = type(self)
        attr = getattr(cls, name)
        if type(attr) is not property:
            e = "%r is not a property"
            e %= name
            e = AttributeError(e)
            raise e
        try:
            object.__setattr__(self, name, value)
        except VersionError:
            raise
        except:
            e = "%r is an invalid value for %r"
            e %= (value, cls.__name__ + "." + name)
            raise VersionError(e)
    
        
