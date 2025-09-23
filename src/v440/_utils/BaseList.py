from abc import ABCMeta, abstractmethod
from typing import *


class BaseList(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    def __bool__(self: Self) -> bool: ...
