from abc import abstractmethod
from typing import *


class BaseList:
    __slots__ = ()

    @abstractmethod
    def isempty(self: Self) -> bool: ...
