from v440.core.VersionError import VersionError
from datahold import OkayABC
from typing import *

class Base:

    def __ge__(self, other, /):
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return other <= self
        return self.data >= other

    __hash__ = OkayABC.__hash__

    def __le__(self, other, /):
        try:
            other = type(self)(other)
        except:
            pass
        else:
            return self._data <= other._data
        return self.data <= other

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, str(self))

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
