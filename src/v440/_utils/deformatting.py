"""Provide the CoreABC abstract base for v440 classes."""

__all__: list[str] = ["Deformat"]

from abc import ABC, abstractmethod
from typing import Self

from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440.errors.VersionError import VersionError


class Deformattable(ABC):
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
