from abc import ABCMeta, abstractmethod
from typing import *

import setdoc


class BaseList(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    @abstractmethod
    def _format(self: Self, format_spec: str) -> str: ...
