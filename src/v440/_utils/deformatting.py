__all__: list[str] = ["OldDeformattable"]

from abc import ABC, abstractmethod
from typing import Any, Self

from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440.errors.VersionError import VersionError


class NewDeformattable(ABC):
    __slots__ = ()

    @classmethod
    @abstractmethod
    def _deformat(cls: type[Self], body: str | None = None, /) -> Any: ...

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        x: str
        y: Any
        y = cls._deformat()
        try:
            for x in set(map(str, strings)):
                y &= cls._deformat(x)
            return y.best()  # type: ignore[no-any-return]
        except VersionError:
            raise
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise VersionError(msg)


class OldDeformattable(ABC):
    __slots__ = ()

    @classmethod
    @abstractmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str: ...

    @classmethod
    def deformat(cls: type[Self], /, *strings: object) -> str:
        msg: str
        info: dict[str, Self]
        x: object
        y: str
        info = dict()
        for x in strings:
            y = str(x)
            info[y] = cls(string=y)  # type: ignore[call-arg]
        try:
            return cls._deformat(info)
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise VersionError(msg)
