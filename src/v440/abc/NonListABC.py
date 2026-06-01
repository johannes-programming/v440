from abc import abstractmethod
from typing import Any, Optional, Self, cast

import cmp3
import setdoc

from v440.abc.CoreABC import CoreABC

__all__ = ["NonListABC"]


class NonListABC(cmp3.CmpABC, CoreABC):
    __slots__ = ()

    @setdoc.basic
    def __cmp__(self: Self, other: Any) -> None | float | int:
        if type(self) is not type(other):
            return None
        return cast(
            float | int, cmp3.cmp(self._cmp(), other._cmp(), mode="le")
        )

    @setdoc.basic
    def __init__(
        self: Self,
        other: Optional[Self] = None,
        /,
        **kwargs: Any,
    ) -> None:
        x: str
        y: Any
        for x, y in self._init_factories().items():
            if other is None:
                object.__setattr__(self, x, y())
            else:
                object.__setattr__(self, x, y(getattr(self, x)))
        self._init_kwargs(**kwargs)

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @classmethod
    @abstractmethod
    def _init_factories(cls: type[Self]) -> dict[str, Any]: ...
