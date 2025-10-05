from typing import *

import setdoc
from datarepr import datarepr
from v440._utils.guarding import guard
from v440._utils.BaseStringer import BaseStringer
import operator
from abc import abstractmethod

__all__ = ["QualStringer"]


class QualStringer(BaseStringer):
    __slots__ = ("_phase", "_num")

    string: str
    phase:str
    num:int

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return self.phase != ""
    
    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(
            type(self).__name__, 
            phase=self.phase,
            num=self.num,
        )
    
    @classmethod
    @abstractmethod
    def _phase_parse(cls:type, value:str) -> str:...
    
    @property
    def num(self:Self) -> int:
        return self._num
    
    @num.setter
    @guard
    def num(self:Self, value:SupportsIndex) -> None:
        y:int = operator.index(value)
        if y < 0:
            raise ValueError
        if y and not self.phase:
            self.string = y
        else:
            self._num = y

    @property
    def phase(self:Self) -> str:
        return self._phase
    
    @phase.setter
    @guard
    def phase(self:Self, value:Any) -> None:
        x:str = self._phase_parse(str(value))
        if self.num and not x:
            self.string = self.num
        else:
            self._phase = x


